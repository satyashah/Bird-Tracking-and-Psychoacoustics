import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


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

    # Now we have the filtered_bird_frame we want to make sure no values are to far from center of mass we will call these outliers

    com = [X_SIZE/2, Y_SIZE/2]  # Set to center of image

    # Get coordinates of all points that are =255
    point_arr = np.argwhere(filtered_bird_frame == 255)
    
    # Run k-means clustering to find the bird versus the background
    kmeans = KMeans(n_clusters=8, random_state=0).fit(point_arr)
    
    # # Plot the k-means clustering
    # plt.scatter(point_arr[:, 1], point_arr[:, 0], c=kmeans.labels_)
    # plt.scatter(kmeans.cluster_centers_[:, 1], kmeans.cluster_centers_[:, 0], c='r')
    # plt.show()

    # Keep all points that are not labeled as outliers (check which group is closest to middle)
    center_group = np.argmin(np.linalg.norm(kmeans.cluster_centers_ - com, axis=1))

    # Keep all points that are in the center group
    for i, label in enumerate(kmeans.labels_):
        if label != center_group:
            filtered_bird_frame[point_arr[i, 0], point_arr[i, 1]] = 0

    # Find center of mass
    com = np.argwhere(filtered_bird_frame == 255).mean(axis=0).astype(int)

    return filtered_bird_frame, com

def get_direction(bird_plot, com):
    """
    This function takes the bird plot and center of mass and returns the angle of the bird.
    """

    # Get the fartherst point from the center of mass
    point_arr = np.argwhere(bird_plot == 255)
    distances = np.linalg.norm(point_arr - com, axis=1)

    # Turn into dictionary where key is the distance and value is the point
    distance_dict = {distances[i]: point_arr[i] for i in range(len(distances))}

    # Sort all keys of distance_dict in descending order
    sorted_distances = sorted(distance_dict.keys())
    print(sorted_distances)

    # Go throught the sorted keys and find the first >3 pixel gap, this is the farthest point
    for i in range(len(sorted_distances) - 1):
        if sorted_distances[i + 1] - sorted_distances[i] > 3:
            farthest_point = distance_dict[sorted_distances[i]]
            break
        if i == len(sorted_distances) - 2:
            farthest_point = distance_dict[sorted_distances[i + 1]]
    
    # Get rid of points in that are farther than the farthest point in point_arr
    for point in point_arr:
        if np.linalg.norm(point - com) > np.linalg.norm(farthest_point - com):
            bird_plot[point[0], point[1]] = 0
    
    
    # plt.imshow(bird_plot, cmap='gray')
    # plt.scatter(farthest_point[1], farthest_point[0], c='r')
    # plt.scatter(com[1], com[0], c='g')
    # plt.show()
    
    # Second time to find the new center of mass and farthest point
    point_arr = np.argwhere(bird_plot == 255)
    com = point_arr.mean(axis=0).astype(int)
    distances = np.linalg.norm(point_arr - com, axis=1)

    # Find the max of distances and the point that corresponds to it
    farthest_point = point_arr[np.argmax(distances)]

    # Get the angle of the bird
    angle = np.arctan2(abs(farthest_point[0] - com[0]), abs(farthest_point[1] - com[1])) * 180 / np.pi
    print("ANGLE:", 90-angle)

    # Plot a line from the center of mass to the farthest point
    plt.imshow(bird_plot, cmap='gray')
    plt.plot([com[1], farthest_point[1]], [com[0], farthest_point[0]], c='r')

    # Plot the distance of all points =255 to the center of mass
    plt.scatter(point_arr[:, 1], point_arr[:, 0], c=distances)
    plt.scatter(com[1], com[0], c='r')
    plt.show()
    
    return None





bird_pos = cv2.imread('test_images/bird_fake_pos.jpg', 0)
bird_neg1 = cv2.imread('test_images/bird_fake_neg.jpg', 0)
bird_neg2 = cv2.imread('test_images/bird_fake_neg2.jpg', 0)
bird_right_less = cv2.imread('test_images/bird_fake_right_less.jpg', 0)
bird_right = cv2.imread('test_images/bird_fake_right.jpg', 0)


bird_img = bird_pos

bird_plot, right_com = get_bird(bird_neg1, bird_img)




# plt.imshow(bird_pos, cmap='gray')
# point_arr = np.argwhere(bird_plot == 255)
# plt.scatter(point_arr[:, 1], point_arr[:, 0], c = 'b')
# plt.scatter(right_com[1], right_com[0], c='r')
# plt.show()



bird_angle = get_direction(bird_plot, right_com)

cv2.destroyAllWindows()





