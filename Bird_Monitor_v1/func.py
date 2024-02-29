import cv2
import numpy as np

def get_clean_image(neg_baseline, img=None, img_path=None):
    """
    This function takes an image path and a negative baseline image of birds and returns the simple bird image.
    """

    if isinstance(img_path, str) and img_path:
        img = cv2.imread(img_path, flags=0)
    elif img is None:
        raise ValueError("Please provide an image path or an image")

    bird_neg = cv2.imread(neg_baseline, 0)

    bird_frame = cv2.absdiff(img, bird_neg)

    resized_bird_frame = cv2.resize(bird_frame, (280, 280)) 
    
    return resized_bird_frame


def detect_pos_line(cleaned_pos_img=None, cleaned_pos_img_path=None):
    """
    This function takes a bird image and returns the average x coordinate of the bird.
    """
    if cleaned_pos_img_path is not None:
        cleaned_pos_img = cv2.imread(cleaned_pos_img_path, flags=0)
    elif cleaned_pos_img is None:
        raise ValueError("Please provide a cleaned image or a cleaned image path")

    coords = np.argwhere(cleaned_pos_img == 1)
    print(coords)

    x_avg = np.mean(coords[:, 0])
    print(x_avg)