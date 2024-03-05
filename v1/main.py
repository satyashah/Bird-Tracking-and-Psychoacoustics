from func import *


print("Running main.py")

bird_pos = cv2.imread('test_images/bird_fake_pos.jpg', 0)
bird_neg1 = cv2.imread('test_images/bird_fake_neg.jpg', 0)
bird_neg2 = cv2.imread('test_images/bird_fake_neg2.jpg', 0)
bird_right_less = cv2.imread('test_images/bird_fake_right_less.jpg', 0)
bird_right = cv2.imread('test_images/bird_fake_right.jpg', 0)

# Show neg baseline
neg_avg, neg_std = get_neg_baseline(bird_neg1, bird_neg2)

# Algorithm that A) cleans out all the noise and B) finds the center of the bird
# bird_pos_plot, pos_com = get_bird(neg_avg, bird_pos)
bird_right_plot, right_com = get_bird(bird_neg1, bird_right)

# Show the images
plt.imshow(bird_right, cmap='gray')

point_arr = np.argwhere(bird_right_plot == 255)
plt.scatter(point_arr[:, 1], point_arr[:, 0], c = 'b')
plt.scatter(right_com[1], right_com[0], c='r')
plt.show()



# # Show the cleaned images
cv2.imshow('Bird Pos', bird_pos)
cv2.imshow('Bird Pos Clean', bird_pos_clean)
# cv2.imshow('Bird Left', bird_left_image)
cv2.waitKey(0)


# # Save the images
# cv2.imwrite('test_images/bird_tube_pos_clean.jpg', bird_pos_image)
# cv2.imwrite('test_images/bird_tube_left_clean.jpg', bird_left_image)



cv2.destroyAllWindows()