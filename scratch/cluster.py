import cv2
import numpy as np

def detect_pieces(image_path):
    image = cv2.imread(image_path)
    if image is None: return

    # Redimensionner comme image_processor.py
    height, width = image.shape[:2]
    max_dim = 2000
    if max(height, width) > max_dim:
        scale = max_dim / max(height, width)
        image = cv2.resize(image, (int(width * scale), int(height * scale)))

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Masques de couleur (les mèmes que j'ai mis)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    mask_red = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), 
                              cv2.inRange(hsv, lower_red2, upper_red2))

    lower_yellow = np.array([15, 50, 80])
    upper_yellow = np.array([40, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, kernel)

    tokens = [] # list of (x, y, color)
    
    for color_mask, color_id in [(mask_red, 1), (mask_yellow, 2)]:
        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            # Find bounding box to check size
            x, y, w, h = cv2.boundingRect(c)
            if area > 100 and 0.5 < w/float(h) < 2.0:
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    tokens.append((cX, cY, color_id, w))

    if not tokens:
        print("No tokens found")
        return

    # Average width of tokens
    avg_w = np.mean([t[3] for t in tokens])
    print(f"Found {len(tokens)} tokens, avg width: {avg_w}")

    # Cluster X
    xs = sorted([t[0] for t in tokens])
    cols_x = []
    for x in xs:
        if not cols_x or x - np.mean(cols_x[-1]) > avg_w * 0.5:
            cols_x.append([x])
        else:
            cols_x[-1].append(x)
    col_centers = [int(np.mean(g)) for g in cols_x]

    # Cluster Y
    ys = sorted([t[1] for t in tokens])
    rows_y = []
    for y in ys:
        if not rows_y or y - np.mean(rows_y[-1]) > avg_w * 0.5:
            rows_y.append([y])
        else:
            rows_y[-1].append(y)
    row_centers = [int(np.mean(g)) for g in rows_y]

    print(f"Detected {len(row_centers)} rows, {len(col_centers)} columns")

    # Create grid
    grid = [[0 for _ in range(len(col_centers))] for _ in range(len(row_centers))]
    
    for t in tokens:
        x, y, color, _ = t
        # Find closest col, row
        c = np.argmin([abs(x - cx) for cx in col_centers])
        r = np.argmin([abs(y - ry) for ry in row_centers])
        grid[r][c] = color

    for row in grid:
        print(" ".join(str(c) for c in row))

detect_pieces('debug_last_image.png')
