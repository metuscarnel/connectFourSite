"""
Image Processor v2 - Robuste et configurableLecture d'image Connect4 9x9 avec détection optimale des pions.
Supporte plusieurs approches: HSV masques, HoughCircles, hybrid.
"""
import cv2
import numpy as np
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROWS = 8
COLS = 9
EMPTY = 0
PLAYER1 = 1  # Rouge
PLAYER2 = 2  # Jaune

# ===== PARAMÈTRES OPTIMISÉS =====
# À ajuster avec calibrate_hsv.py si images BGA particulières

# RED - double plage HSV (teinte cyclique 0-180)
RED_PARAMS = {
    'lower1': np.array([0, 100, 50]),
    'upper1': np.array([10, 255, 255]),
    'lower2': np.array([160, 100, 50]),
    'upper2': np.array([180, 255, 255]),
}

# YELLOW (seuils stricts pour éviter faux positifs)
YELLOW_PARAMS = {
    'lower': np.array([15, 120, 100]),  # S≥120, V≥100 pour saturation/luminosité élevée
    'upper': np.array([35, 255, 255]),
}

# BLUE (pour détecter le plateau)
BLUE_PARAMS = {
    'lower': np.array([85, 40, 40]),
    'upper': np.array([145, 255, 255]),
}

MORPHO_KERNEL_SIZE = 5  # 5x5 pour réduction bruit robuste
DETECTION_THRESHOLD = 0.35  # 35% pour réduire faux positifs


def process_connect4_image(image_bytes, debug=False):
    """
    Analyse une image de Connect4 9x9 et retourne la grille.
    
    Args:
        image_bytes: Bytes de l'image
        debug: Si True, affiche les étapes intermédiaires
    
    Returns:
        grid: Liste 8x9 avec EMPTY(0), PLAYER1(1), PLAYER2(2)
    """
    try:
        # Décodage
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            logger.error("Impossible de décoder l'image OpenCV")
            raise ValueError("Image invalide")
        
        logger.info(f"Image décodée: {image.shape}")
        
        # Redimensionnement si trop grand
        height, width = image.shape[:2]
        if max(height, width) > 2000:
            scale = 2000 / max(height, width)
            image = cv2.resize(image, (int(width * scale), int(height * scale)))
            logger.info(f"Image redimensionnée à {image.shape}")
        
        # Détection du plateau bleu
        image_cropped = _crop_to_board(image, debug=debug)
        
        # Stratégie 1: Détection HSV classique
        grid = _detect_with_hsv(image_cropped, debug=debug)
        
        # Stratégie 2: Si HSV donne résultats bizarres, essayer HoughCircles
        if _is_grid_suspicious(grid):
            logger.warning("Grille suspecte, tentative HoughCircles...")
            grid_circles = _detect_with_hough_circles(image_cropped)
            if grid_circles is not None and not _is_grid_suspicious(grid_circles):
                grid = grid_circles
                logger.info("✅ HoughCircles a donné meilleur résultat")
        
        return grid
        
    except Exception as e:
        logger.error(f"Erreur traitement image: {e}", exc_info=True)
        raise


def _crop_to_board(image, debug=False):
    """
    Isole le plateau bleu du reste de l'image.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Masque bleu
    mask_blue = cv2.inRange(hsv, BLUE_PARAMS['lower'], BLUE_PARAMS['upper'])
    
    # Trouver le plus grand contour bleu
    contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        logger.warning("⚠️  Plateau bleu non détecté, utilisation image complète")
        return image
    
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    area_ratio = (w * h) / (image.shape[0] * image.shape[1])
    
    # Vérifier que le plateau occupe au least 30% de l'image
    if area_ratio < 0.3:
        logger.warning(f"⚠️  Plateau occupe {area_ratio*100:.1f}%, utilisation image complète")
        return image
    
    # Cropper avec petite marge
    margin = max(1, int(w * 0.01))
    cropped = image[y+margin:y+h-margin, x+margin:x+w-margin]
    logger.info(f"Plateau isolé: {cropped.shape} (ratio {area_ratio*100:.1f}%)")
    
    return cropped


def _detect_with_hsv(image, debug=False):
    """
    Détection classique par masques HSV.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, w = image.shape[:2]
    
    # Masques de couleur
    mask_red1 = cv2.inRange(hsv, RED_PARAMS['lower1'], RED_PARAMS['upper1'])
    mask_red2 = cv2.inRange(hsv, RED_PARAMS['lower2'], RED_PARAMS['upper2'])
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    
    mask_yellow = cv2.inRange(hsv, YELLOW_PARAMS['lower'], YELLOW_PARAMS['upper'])
    
    # Morphologie
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (MORPHO_KERNEL_SIZE, MORPHO_KERNEL_SIZE))
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, kernel)
    
    # Grille vide
    grid = [[EMPTY] * COLS for _ in range(ROWS)]
    
    # Analyse cellule par cellule
    cell_h = h / ROWS
    cell_w = w / COLS
    
    for row in range(ROWS):
        for col in range(COLS):
            # ROI centrale (40% de la cellule, exclut 30% des bords)
            y_start = int(row * cell_h + cell_h * 0.3)
            y_end = int((row + 1) * cell_h - cell_h * 0.3)
            x_start = int(col * cell_w + cell_w * 0.3)
            x_end = int((col + 1) * cell_w - cell_w * 0.3)
            
            roi_red = mask_red[y_start:y_end, x_start:x_end]
            roi_yellow = mask_yellow[y_start:y_end, x_start:x_end]
            
            red_count = cv2.countNonZero(roi_red)
            yellow_count = cv2.countNonZero(roi_yellow)
            total_pixels = max(1, (y_end - y_start) * (x_end - x_start))
            
            red_ratio = red_count / total_pixels
            yellow_ratio = yellow_count / total_pixels
            
            # Détection avec seuil et priorité
            if red_ratio > DETECTION_THRESHOLD and red_ratio > yellow_ratio:
                grid[row][col] = PLAYER1
            elif yellow_ratio > DETECTION_THRESHOLD:
                grid[row][col] = PLAYER2
    
    logger.info(f"HSV: {sum(sum(1 for c in row if c == PLAYER1) for row in grid)} rouges, "
                f"{sum(sum(1 for c in row if c == PLAYER2) for row in grid)} jaunes")
    
    return grid


def _detect_with_hough_circles(image):
    """
    Détection alternative via HoughCircles (fallback si HSV mauvais).
    """
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        
        h, w = image.shape[:2]
        expected_radius = min(w // (2 * COLS), h // (2 * ROWS))
        
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, dp=1,
            minDist=expected_radius,
            param1=50, param2=20,
            minRadius=int(expected_radius * 0.6),
            maxRadius=int(expected_radius * 1.4)
        )
        
        if circles is None:
            logger.warning("HoughCircles: Aucun cercle détecté")
            return None
        
        circles = np.uint16(np.around(circles))[0, :]
        logger.info(f"HoughCircles: {len(circles)} cercles détectés")
        
        # Organisation en grille
        xs = sorted([c[0] for c in circles])
        ys = sorted([c[1] for c in circles])
        
        # Clustering par position
        col_centers = _cluster_positions(xs, expected_radius)
        row_centers = _cluster_positions(ys, expected_radius)
        
        logger.info(f"Grille: {len(row_centers)} lignes x {len(col_centers)} colonnes")
        
        if len(row_centers) != ROWS or len(col_centers) != COLS:
            logger.warning(f"Dimensions mismatch: attendu {ROWS}x{COLS}, trouvé {len(row_centers)}x{len(col_centers)}")
            return None
        
        # Construction grille avec couleurs
        grid = [[EMPTY] * COLS for _ in range(ROWS)]
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        for circle in circles:
            x, y, r = circle
            
            # Trouver ligne/col
            row = min(range(len(row_centers)), key=lambda i: abs(y - row_centers[i]))
            col = min(range(len(col_centers)), key=lambda i: abs(x - col_centers[i]))
            
            # Déterminer couleur
            roi = hsv[max(0, y-r):min(hsv.shape[0], y+r),
                      max(0, x-r):min(hsv.shape[1], x+r)]
            
            if roi.size == 0:
                continue
            
            # Compter pixels de chaque couleur
            mask_red1 = cv2.inRange(roi, RED_PARAMS['lower1'], RED_PARAMS['upper1'])
            mask_red2 = cv2.inRange(roi, RED_PARAMS['lower2'], RED_PARAMS['upper2'])
            mask_yellow = cv2.inRange(roi, YELLOW_PARAMS['lower'], YELLOW_PARAMS['upper'])
            
            red_count = cv2.countNonZero(mask_red1) + cv2.countNonZero(mask_red2)
            yellow_count = cv2.countNonZero(mask_yellow)
            
            if red_count > yellow_count and red_count > 0:
                grid[row][col] = PLAYER1
            elif yellow_count > 0:
                grid[row][col] = PLAYER2
        
        logger.info(f"HoughCircles result: {sum(sum(1 for c in row if c == PLAYER1) for row in grid)} rouges, "
                    f"{sum(sum(1 for c in row if c == PLAYER2) for row in grid)} jaunes")
        
        return grid
        
    except Exception as e:
        logger.error(f"HoughCircles failed: {e}")
        return None


def _cluster_positions(positions, min_distance):
    """
    Regroupe les positions proches (clustering).
    """
    if not positions:
        return []
    
    clusters = [[positions[0]]]
    for pos in positions[1:]:
        if pos - clusters[-1][-1] > min_distance:
            clusters.append([pos])
        else:
            clusters[-1].append(pos)
    
    return [int(np.mean(cluster)) for cluster in clusters]


def _is_grid_suspicious(grid):
    """
    Détecte les grilles suspectes (peu de pions, ou trop).
    """
    total = sum(sum(1 for c in row if c != EMPTY) for row in grid)
    
    # Trop peu ou trop (jeu complet aurait max 72 pions en 9x9)
    if total < 2 or total > 72:
        logger.warning(f"⚠️  Grille suspecte: {total} pions détectés")
        return True
    
    return False
