import cv2
import numpy as np

img = cv2.imread('debug_last_image.png')
h, w = img.shape[:2]
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5)

expected_r = min(w//7, h//6) // 2

circles = cv2.HoughCircles(
    gray, cv2.HOUGH_GRADIENT, dp=1, minDist=expected_r,
    param1=50, param2=20, minRadius=int(expected_r*0.5), maxRadius=int(expected_r*1.5)
)

circles = np.uint16(np.around(circles))[0, :]
xs = sorted([c[0] for c in circles])
ys = sorted([c[1] for c in circles])

cols_x = []
for x in xs:
    if not cols_x or x - cols_x[-1][-1] > expected_r:
        cols_x.append([x])
    else:
        cols_x[-1].append(x)
col_centers = [int(np.mean(group)) for group in cols_x]

rows_y = []
for y in ys:
    if not rows_y or y - rows_y[-1][-1] > expected_r:
        rows_y.append([y])
    else:
        rows_y[-1].append(y)
row_centers = [int(np.mean(group)) for group in rows_y]

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
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

grid = []
for y in row_centers:
    row_tokens = []
    for x in col_centers:
        y_start, y_end = int(y - expected_r*0.6), int(y + expected_r*0.6)
        x_start, x_end = int(x - expected_r*0.6), int(x + expected_r*0.6)
        y_start, y_end = max(0, y_start), min(h, y_end)
        x_start, x_end = max(0, x_start), min(w, x_end)
        
        roi_red = mask_red[y_start:y_end, x_start:x_end]
        roi_yellow = mask_yellow[y_start:y_end, x_start:x_end]
        
        red_pixels = cv2.countNonZero(roi_red)
        yellow_pixels = cv2.countNonZero(roi_yellow)
        total = max(1, (y_end - y_start) * (x_end - x_start))
        
        if red_pixels/total > 0.3 and red_pixels > yellow_pixels:
            row_tokens.append('R')
        elif yellow_pixels/total > 0.3:
            row_tokens.append('Y')
        else:
            row_tokens.append('.')
    grid.append(row_tokens)

for r in grid:
    print(" ".join(r))
