from func import *
import cv2
import numpy as np
import matplotlib.pyplot as plt

print("Running main.py")

bird_pos = cv2.imread('test_images/bird_fake_pos.jpg', 0)
bird_neg1 = cv2.imread('test_images/bird_fake_neg.jpg', 0)
bird_neg2 = cv2.imread('test_images/bird_fake_neg2.jpg', 0)
bird_right_less = cv2.imread('test_images/bird_fake_right_less.jpg', 0)
bird_right = cv2.imread('test_images/bird_fake_right.jpg', 0)

# Show neg baseline




neg_avg, neg_std = get_neg_baseline(bird_neg1, bird_neg2)
print(neg_avg)

cv2.imshow('Neg Baseline', neg_avg)
cv2.waitKey(0)

bird_pos_image = get_clean_image(bird_neg1, neg_std, bird_pos)
bird_left_image = get_clean_image(bird_neg1, neg_std, bird_right)


# # Show the cleaned images
# cv2.imshow('Bird Pos', bird_pos_image)
# cv2.imshow('Bird Left', bird_left_image)
# cv2.waitKey(0)


# # Save the images
# cv2.imwrite('test_images/bird_tube_pos_clean.jpg', bird_pos_image)
# cv2.imwrite('test_images/bird_tube_left_clean.jpg', bird_left_image)



cv2.destroyAllWindows()