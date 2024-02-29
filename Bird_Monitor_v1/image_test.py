import cv2 as cv

bird_pos = cv.imread('test_images/bird_pos.jpg', 0)
bird_neg1 = cv.imread('test_images/bird_neg1.jpg', 0)
bird_neg2 = cv.imread('test_images/bird_neg2.jpg', 0)
bird_left = cv.imread('test_images/bird_left.jpg', 0)
bird_right = cv.imread('test_images/bird_right.jpg', 0)

# Shows the images
# cv.imshow('+ Baseline', bl_mouse)
# cv.imshow('- Baseline', bl_no_mouse)
# cv.imshow('Right', right_mouse)
# cv.imshow('Left', left_mouse)


# Calculate pixel-wise absolute difference between neg baseline to see natural variation
variation_per_measurement = cv.absdiff(bird_neg1, bird_neg2)

# Display the frames and the pixel difference plot
# cv.imshow('Pixel Difference', noise_frame)
print("Variation: \n", variation_per_measurement)


# Subtract the negative baseline from the positive baseline to get the bird
bird_frame = cv.absdiff(bird_pos, bird_neg1)

# Display the frames and the pixel difference plot
cv.imshow('Bird Frame', bird_frame)



cv.waitKey(0) 
cv.destroyAllWindows()



