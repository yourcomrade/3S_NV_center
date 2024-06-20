import numpy as np
import cv2
import matplotlib.pyplot as plt

# Function to find the ROI where the light is hitting the lens
def find_roi(image):
    # Convert the image to grayscale if it's not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Apply a threshold to get a binary image
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If no contours are found, return a default ROI
    if not contours:
        return (0, 0, image.shape[1], image.shape[0])

    # Find the largest contour
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    return (x, y, w, h)

# Load the image from a file
image_path = "C:\Users\abene\Documents\GitHub Repositories\3S_NV_center\Camera\region-of-interest\Laser-test-image.png"
image = cv2.imread(image_path)  # Replace 'test_image.jpg' with your image file

# Ensure the image is loaded correctly
if image is None:
    print("Error: Unable to load image.")
    exit()

# Find the ROI
roi = find_roi(image)
x, y, w, h = roi

# Draw a rectangle around the detected ROI
cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

# Display the original image with the ROI highlighted
cv2.imshow('Detected ROI', image)

# Wait until a key is pressed, then close the image window
cv2.waitKey(0)
cv2.destroyAllWindows()

# Optionally, save the result to a file
cv2.imwrite('detected_roi.jpg', image)  # Replace 'detected_roi.jpg' with your desired output file name
