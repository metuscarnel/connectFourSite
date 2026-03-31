import cv2
import numpy as np

image = cv2.imread('debug_last_image.png')
print(f"Original image shape: {image.shape}")
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

lower_blue = np.array([90, 50, 50])
upper_blue = np.array([140, 255, 255])
mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
if contours:
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h_box = cv2.boundingRect(largest_contour)
    if w * h_box > 0.1 * image.shape[0] * image.shape[1]:
        print(f"Blue mask rect found: {x}, {y}, {w}, {h_box} (Area: {w*h_box})")
        margin = max(1, int(w * 0.01))
        image = image[y+margin:y+h_box-margin, x+margin:x+w-margin]
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    else:
        print("Blue mask rect too small")

h, w = image.shape[:2]
ROWS = 8
COLS = 9
cell_h = h / ROWS
cell_w = w / COLS
print(f"Cropped image shape: {h}x{w}. Cell sizes: h={cell_h:.2f}, w={cell_w:.2f}")

lower_red1 = np.array([0, 70, 50])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([160, 70, 50])
upper_red2 = np.array([180, 255, 255])
mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
mask_red = cv2.bitwise_or(mask_red1, mask_red2)

lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([35, 255, 255])
mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]

for row in range(ROWS):
    for col in range(COLS):
        y_start = int(row * cell_h + cell_h * 0.3)
        y_end = int((row + 1) * cell_h - cell_h * 0.3)
        x_start = int(col * cell_w + cell_w * 0.3)
        x_end = int((col + 1) * cell_w - cell_w * 0.3)
        roi_red = mask_red[y_start:y_end, x_start:x_end]
        roi_yellow = mask_yellow[y_start:y_end, x_start:x_end]
        red_pixels = cv2.countNonZero(roi_red)
        yellow_pixels = cv2.countNonZero(roi_yellow)
        total = (y_end - y_start) * (x_end - x_start)
        rR = red_pixels / max(1, total)
        yR = yellow_pixels / max(1, total)
        
        if rR > 0.25 and rR > yR:
            grid[row][col] = 'R'
        elif yR > 0.25:
            grid[row][col] = 'Y'
            
        print(f"[{row},{col}] R:{rR:.3f} Y:{yR:.3f} -> {grid[row][col]}")

for r in range(ROWS):
    print(" ".join(grid[r]))
