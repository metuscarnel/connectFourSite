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
        
    # Redimensionnement optionnel (limite portée à 2000px pour garder la netteté)
    height, width = image.shape[:2]
    max_dim = 2000
    if max(height, width) > max_dim:
        scale = max_dim / max(height, width)
        image = cv2.resize(image, (int(width * scale), int(height * scale)))
        
    return _grid_detection(image)

def _grid_detection(image):
    """
    Détection robuste du plateau basée sur le découpage de l'image (si un cadre bleu est détecté).
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 1. Isoler le plateau bleu pour l'aligner parfaitement
    lower_blue = np.array([85, 40, 40])      # Réduit les minima pour capturer des bleus moins saturés
    upper_blue = np.array([145, 255, 255])   # Légèrement élargi
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    
    contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h_box = cv2.boundingRect(largest_contour)
        # Vérification : le plateau bleu doit occuper au moins 40% de l'image (réduit de 50% pour plus de flexibilité)
        if w * h_box > 0.4 * image.shape[0] * image.shape[1]:
            margin = max(1, int(w * 0.01))
            image = image[y+margin:y+h_box-margin, x+margin:x+w-margin]
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    h, w = image.shape[:2]
    cell_h = h / ROWS
    cell_w = w / COLS
    
    # 2. Masques de couleur pour les pions (plages élargies pour meilleureétection)
    # ROUGE : teintes 0-10 et 160-180 (HSV cyclique)
    lower_red1 = np.array([0, 100, 50])      # Réduit saturation min pour capturer teintes pâles
    upper_red1 = np.array([12, 255, 255])   
    lower_red2 = np.array([158, 100, 50])   
    upper_red2 = np.array([180, 255, 255])
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)

    # JAUNE : teintes 15-40 (plage restrictive pour éviter faux positifs du fond)
    lower_yellow = np.array([15, 120, 100])  # S≥120 pour exclure fond pâle, V≥100 pour saturation
    upper_yellow = np.array([35, 255, 255])  # H réduit à 35 pour éviter teintes vertes
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Érosion/Dilatation pour réduire le bruit (kernel 5x5 pour plus agressif)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, kernel)
    
    grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
    
    # 3. Échantillonner chaque cellule pour déterminer s'il y a un pion rouge ou jaune
    for row in range(ROWS):
        for col in range(COLS):
            # Zone centrale de 40% (exclut les bords à 30%)
            y_start = int(row * cell_h + cell_h * 0.3)
            y_end = int((row + 1) * cell_h - cell_h * 0.3)
            x_start = int(col * cell_w + cell_w * 0.3)
            x_end = int((col + 1) * cell_w - cell_w * 0.3)
            
            roi_red = mask_red[y_start:y_end, x_start:x_end]
            roi_yellow = mask_yellow[y_start:y_end, x_start:x_end]
            
            red_pixels = cv2.countNonZero(roi_red)
            yellow_pixels = cv2.countNonZero(roi_yellow)
            
            total = max(1, (y_end - y_start) * (x_end - x_start))
            
            rR = red_pixels / total
            yR = yellow_pixels / total
            
            # Détection : plus de 35% de la couleur détectée au centre = Pion identifié
            # Threshold élevé (35%) réduit les faux positifs du fond
            if rR > 0.35 and rR > yR:
                grid[row][col] = PLAYER1
            elif yR > 0.35 and yR >= rR:
                grid[row][col] = PLAYER2
                
    return grid
