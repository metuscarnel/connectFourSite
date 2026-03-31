import cv2
import numpy as np

ROWS = 8
COLS = 9
EMPTY = 0
PLAYER1 = 1  # Rouge
PLAYER2 = 2  # Jaune

def process_connect4_image(image_bytes):
    """
    Analyse une image de puissance 4 et renvoie une matrice (ROWSxCOLS).
    Convention: Ligne 0 = Haut du plateau (visuellement).
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("Impossible de décoder l'image OpenCV.")
        
    # Redimensionnement optionnel pour éviter les traitements lourds
    height, width = image.shape[:2]
    max_dim = 1000
    if max(height, width) > max_dim:
        scale = max_dim / max(height, width)
        image = cv2.resize(image, (int(width * scale), int(height * scale)))
        
    return _fallback_grid_detection(image)

def _fallback_grid_detection(image):
    """
    Détection universelle du plateau via détection de cercles (Hough).
    S'adapte dynamiquement au nombre de lignes et colonnes de l'image.
    """
    h, w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)

    # Paramètres approximatifs : on cherche +- 7 colonnes ou 6 lignes
    expected_r = min(w//7, h//6) // 2

    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1, minDist=expected_r,
        param1=50, param2=20, minRadius=int(expected_r*0.5), maxRadius=int(expected_r*1.5)
    )

    # Si aucun cercle trouvé, on retourne une grille vide pour éviter le crash
    if circles is None:
        return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

    circles = np.uint16(np.around(circles))[0, :]
    
    # Extraire les coordonnées X et Y de tous les cercles trouvés
    xs = sorted([c[0] for c in circles])
    ys = sorted([c[1] for c in circles])

    # Grouper les X pour trouver les colonnes
    cols_x = []
    for x in xs:
        if not cols_x or x - cols_x[-1][-1] > expected_r:
            cols_x.append([x])
        else:
            cols_x[-1].append(x)
    col_centers = [int(np.mean(group)) for group in cols_x]

    # Grouper les Y pour trouver les lignes
    rows_y = []
    for y in ys:
        if not rows_y or y - rows_y[-1][-1] > expected_r:
            rows_y.append([y])
        else:
            rows_y[-1].append(y)
    row_centers = [int(np.mean(group)) for group in rows_y]

    # Préparation des masques de couleur pour vérifier l'intérieur de chaque cercle
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Rouge (deux plages HSV)
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 70, 50])
    upper_red2 = np.array([180, 255, 255])
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # Jaune
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    grid = []
    
    for y in row_centers:
        row_tokens = []
        for x in col_centers:
            # Échantillonner une petite zone au centre du cercle
            y_start, y_end = int(y - expected_r*0.6), int(y + expected_r*0.6)
            x_start, x_end = int(x - expected_r*0.6), int(x + expected_r*0.6)
            y_start, y_end = max(0, y_start), min(h, y_end)
            x_start, x_end = max(0, x_start), min(w, x_end)
            
            roi_red = mask_red[y_start:y_end, x_start:x_end]
            roi_yellow = mask_yellow[y_start:y_end, x_start:x_end]
            
            red_pixels = cv2.countNonZero(roi_red)
            yellow_pixels = cv2.countNonZero(roi_yellow)
            
            total = max(1, (y_end - y_start) * (x_end - x_start))
            
            rR = red_pixels / total
            yR = yellow_pixels / total
            
            # Seuil de 30% pour valider une couleur
            if rR > 0.3 and rR > yR:
                row_tokens.append(PLAYER1)
            elif yR > 0.3:
                row_tokens.append(PLAYER2)
            else:
                row_tokens.append(EMPTY)
                
        grid.append(row_tokens)

    return grid
