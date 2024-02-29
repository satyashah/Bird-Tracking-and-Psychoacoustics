import cv2


# Read the original image
img = cv2.imread('test_images/TEST.jpg',flags=0) 
cv2.imshow('Original Image', img)
# Blur the image for better edge detection
img_blur = cv2.GaussianBlur(img, (3,3), sigmaX=0, sigmaY=0) 

# Canny Edge Detection
edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=300) 

# Print index location in edges array where the value is not 0
print(edges.nonzero())


 
# Display Canny Edge Detection Image
cv2.imshow('Canny Edge Detection', edges)
cv2.waitKey(0)