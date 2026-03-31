import cv2
import numpy as np

img = cv2.imread('debug_last_image.png')
h, w = img.shape[:2]

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5)

expected_r = min(w//7, h//6) // 2

circles = cv2.HoughCircles(
    gray, cv2.HOUGH_GRADIENT, dp=1, minDist=expected_r,
    param1=50, param2=20, minRadius=int(expected_r*0.6), maxRadius=int(expected_r*1.4)
)

if circles is not None:
    circles = np.uint16(np.around(circles))[0, :]
    print(f"Found {len(circles)} circles")
    
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
    
    print(f"Detected {len(row_centers)} rows: {row_centers}")
    print(f"Detected {len(col_centers)} cols: {col_centers}")
else:
    print("No circles found")
