import numpy as np
import cv2 as cv
import time

cap = cv.VideoCapture(0, cv.CAP_DSHOW)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

#Discard first frame due to darkening
ret, disc_frame = cap.read()


# Capture the first frame
ret, prev_frame = cap.read()
if not ret:
    print("Can't receive frame (stream end?). Exiting ...")
    exit()

# Wait for 2 seconds
time.sleep(2)

# Capture the second frame
ret, curr_frame = cap.read()
if not ret:
    print("Can't receive frame (stream end?). Exiting ...")
    exit()

# Wait for 2 seconds
time.sleep(2)

# Capture the second frame
ret, curr_frame2 = cap.read()
if not ret:
    print("Can't receive frame (stream end?). Exiting ...")
    exit()

# Convert to grayscale (not nessecary)
prev_frame_gray = cv.cvtColor(prev_frame, cv.COLOR_BGR2GRAY)
curr_frame_gray = cv.cvtColor(curr_frame, cv.COLOR_BGR2GRAY)

# Calculate pixel-wise absolute difference
diff_frame = cv.absdiff(curr_frame_gray, prev_frame_gray)

# Display the frames and the pixel difference plot
cv.imshow('Previous Frame', prev_frame_gray)
cv.imshow('Current Frame', curr_frame_gray)
cv.imshow('Pixel Difference', diff_frame)

# Get pixel values for the difference frame
prev_frame_array = np.array(prev_frame_gray)
diff_frame_array = np.array(diff_frame)

# Print the array of pixel values
print(prev_frame_array)

print("Array of pixel values for the difference frame:")
print(diff_frame_array)

cv.waitKey(0)

# Release the capture
cap.release()
cv.destroyAllWindows()
