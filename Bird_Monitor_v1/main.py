from func import *

print("Running main.py")


bird_pos_image = get_clean_image('test_images/blank.jpg', img_path='test_images/bird_tube_pos.jpg')
bird_left_image = get_clean_image('test_images/blank.jpg', img_path='test_images/bird_tube_left.jpg')



cv2.imshow('Bird Pos', bird_pos_image)
cv2.imshow('Bird Left', bird_left_image)
cv2.waitKey(0)


# Save the images
cv2.imwrite('test_images/bird_tube_pos_clean.jpg', bird_pos_image)
cv2.imwrite('test_images/bird_tube_left_clean.jpg', bird_left_image)


cv2.destroyAllWindows()