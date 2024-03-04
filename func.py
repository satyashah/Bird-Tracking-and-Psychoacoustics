import cv2
import numpy as np

def get_neg_baseline(neg1, neg2):
    """
    This function takes two negative baseline images and returns the average and std of the two.
    """
    neg_std = np.mean(np.array(cv2.absdiff(neg1, neg2)))
    neg_baseline = np.mean(np.array([neg1, neg2]), axis=0).round()
    return neg_baseline, neg_std

def get_clean_image(neg_baseline, neg_std, img):
    """
    This function takes an image path and a negative baseline image of birds and returns the simple bird image.
    """

    print("Shape of img:", img.shape)
    print("Shape of neg_baseline:", neg_baseline.shape)
    bird_frame = cv2.absdiff(img, neg_baseline)

    resized_bird_frame = cv2.resize(bird_frame, (280, 280)) 
    
    return resized_bird_frame


def detect_pos_line(cleaned_pos_img):
    """
    This function takes a bird image and returns the average x coordinate of the bird.
    """
    
    coords = np.argwhere(cleaned_pos_img == 1)
    print(coords)

    x_avg = np.mean(coords[:, 0])
    print(x_avg)