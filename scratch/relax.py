import cv2
import numpy as np

img = cv2.imread('debug_last_image.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5)

# Try a wide search for circles
circles = cv2.HoughCircles(
    gray, cv2.HOUGH_GRADIENT, dp=1.0, minDist=20,
    param1=50, param2=15, minRadius=10, maxRadius=60
)

if circles is not None:
    circles = np.uint16(np.around(circles))[0, :]
    print(f"Relaxed found {len(circles)} circles")
    # check valid circles
    good = []
    for c in circles:
        x, y, r = c
        good.append(c)
    print(f"Valid circles {len(good)}")
    output = img.copy()
    for i in good:
        cv2.circle(output, (i[0], i[1]), i[2], (0, 255, 0), 2)
    cv2.imwrite("scratch/annotated_relax.jpg", output)
else:
    print("None")
