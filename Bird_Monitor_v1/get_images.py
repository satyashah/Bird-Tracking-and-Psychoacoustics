import cv2
import os

# Open the webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

#Discard first frame due to darkening
ret, disc_frame = cap.read()

# Capture the first frame in black and white
ret, frame = cap.read()


# Display the frame
# cv2.imshow("Frame", frame)
# cv2.waitKey(0)

# # Prompt the user to enter a name for the image
image_name = "bird_neg2"

# # Print the shape of the frame
print(frame.shape)

# # Prompt the user to enter the coordinates for cropping
x = 150
y = 105
width = 280
height = 280

# # Crop the frame based on the specified coordinates
cropped_frame = frame[y:y+height, x:x+width]

# # Save the cropped frame as an image in the test_images folder
cv2.imwrite(f"test_images/{image_name}.jpg", cropped_frame)

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
