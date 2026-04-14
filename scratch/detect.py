import cv2
import numpy as np

def find_circles_robust(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Error reading image")
        return
        
    h, w = img.shape[:2]
    # Resize if too large
    max_dim = 800
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
        h, w = img.shape[:2]

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply median blur to reduce noise
    gray = cv2.medianBlur(gray, 5)
    
    # Try different Circle detection parameters
    # We expect roughly 6 rows and 7 columns, so radius is roughly w/14
    expected_r = min(w//7, h//6) // 2
    
    print(f"Image shape: {h}x{w}, Expected R: {expected_r}")
    
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=expected_r * 1.5,
        param1=50, param2=30, minRadius=int(expected_r * 0.5), maxRadius=int(expected_r * 1.5)
    )
    
    # If not found, try finding circular contours using thresholding
    if circles is not None:
        circles = np.uint16(np.around(circles))[0, :]
        print(f"HoughCircles found {len(circles)} circles")
        output = img.copy()
        for i in circles:
            cv2.circle(output, (i[0], i[1]), i[2], (0, 255, 0), 2)
            cv2.circle(output, (i[0], i[1]), 2, (0, 0, 255), 3)
        cv2.imwrite("scratch/annotated_hough.jpg", output)
    else:
        print("HoughCircles found no circles")

    # Alternative: Color thresholding to find holes/tokens
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Detect Red, Yellow, and Blue (background)
    mask_blue = cv2.inRange(hsv, np.array([90, 50, 50]), np.array([140, 255, 255]))
    
    # The holes are NOT blue. So invert the blue mask!
    mask_not_blue = cv2.bitwise_not(mask_blue)
    
    # Find contours on the non-blue areas
    contours, _ = cv2.findContours(mask_not_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_contours = []
    output_contours = img.copy()
    for c in contours:
        area = cv2.contourArea(c)
        if area > (expected_r * 0.5)**2 * np.pi and area < (expected_r * 2)**2 * np.pi:
            # Check circularity
            perimeter = cv2.arcLength(c, True)
            if perimeter == 0: continue
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            if circularity > 0.6:  # roughly circular
                valid_contours.append(c)
                cv2.drawContours(output_contours, [c], -1, (255, 0, 0), 2)
                
    print(f"Contour method found {len(valid_contours)} circular regions")
    cv2.imwrite("scratch/annotated_contours.jpg", output_contours)

find_circles_robust('debug_last_image.png')
