import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def get_neg_baseline(neg1, neg2):
    """
    This function takes two negative baseline images and returns the average and std of the two.

    Inputs: Two negative baseline images
    Outputs: The average image of the two images and the standard deviation of the two images
    """
    neg_std = np.mean(np.array(cv2.absdiff(neg1, neg2)))
    neg_baseline = np.mean(np.array([neg1, neg2]), axis=0).round().astype('uint8') # Saves as an array of ints
    neg_baseline = cv2.cvtColor(neg_baseline, cv2.COLOR_GRAY2BGR) # Converts into an image for CV2
    return neg_baseline, neg_std

def get_bird(neg_baseline, img):
    """
    This function takes the image and negative baseline image of birds and returns the bird plot and center of the bird.
    """

    X_SIZE = 280
    Y_SIZE = 280

    bird_frame = cv2.absdiff(img, neg_baseline)

    resized_bird_frame = cv2.resize(bird_frame, (X_SIZE, Y_SIZE)) 

    # Thresholding
    # image of interest, threshold value, what value to set too if above threshold, type of threshold
    threshold_value = 20
    _, filtered_bird_frame = cv2.threshold(resized_bird_frame, threshold_value, 255, cv2.THRESH_BINARY)
    print(filtered_bird_frame)

    # Now we have the filtered_bird_frame we want to make sure no values are to far from center of mass we will call these outliers

    com = [X_SIZE/2, Y_SIZE/2]  # Set to center of image
    #Get distance of all points that are =255 from center of mass Finda all distances that are outliers and sets them to 0 on filtered_bird_frame

    # Get coordinates of all points that are =255
    point_arr = np.argwhere(filtered_bird_frame == 255)

    # Run k-means clustering to find the bird versus the background
    kmeans = KMeans(n_clusters=3, random_state=0).fit(point_arr)
    print(kmeans.labels_)
    print(kmeans.cluster_centers_)
    
    # Plot the k-means clustering
    plt.scatter(point_arr[:, 1], point_arr[:, 0], c=kmeans.labels_)
    plt.scatter(kmeans.cluster_centers_[:, 1], kmeans.cluster_centers_[:, 0], c='r')
    plt.show()

    # Keep all points that are not labeled as outliers (check which group is closest to middle)
    # Find the group that is closest to the middle
    center_group = np.argmin(np.linalg.norm(kmeans.cluster_centers_ - com, axis=1))
    # print(center_group)

    # Keep all points that are in the center group
    for i, label in enumerate(kmeans.labels_):
        if label != center_group:
            filtered_bird_frame[point_arr[i, 0], point_arr[i, 1]] = 0
    


    # Find center of mass
    com = np.argwhere(filtered_bird_frame == 255).mean(axis=0).astype(int)
    # print(com)

    # plt.imshow(img, cmap='gray')
    # plt.scatter(com[1], com[0], c='r')
    # plt.show()


    return filtered_bird_frame, com


def detect_pos_line(cleaned_pos_img):
    """
    This function takes a bird image and returns the average x coordinate of the bird.
    """
    
    coords = np.argwhere(cleaned_pos_img == 1)
    print(coords)

    x_avg = np.mean(coords[:, 0])
    print(x_avg)