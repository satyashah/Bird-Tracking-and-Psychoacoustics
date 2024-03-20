import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import time
from scipy.spatial import ConvexHull

def crop(X_SIZE, Y_SIZE, x_bias, y_bias, img):
    """
    This function takes an image and returns a cropped version of the image.
    """

    # Calculate center coordinates with bias
    center_x = img.shape[1] // 2 + x_bias
    center_y = img.shape[0] // 2 + y_bias

    # Calculate crop boundaries
    crop_x1 = max(0, center_x - X_SIZE // 2)
    crop_x2 = min(img.shape[1], center_x + X_SIZE // 2)
    crop_y1 = max(0, center_y - Y_SIZE // 2)
    crop_y2 = min(img.shape[0], center_y + Y_SIZE // 2)

    cropped_img = img[crop_y1:crop_y2, crop_x1:crop_x2]

    return cropped_img

def get_bird(neg_baseline, img):
    """
    This function takes the image and negative baseline image of birds and returns the bird plot and center of the bird.
    """

    X_SIZE = 700
    Y_SIZE = 700

    resized_bird_frame = crop(X_SIZE, Y_SIZE, -150, 70, img)
    
    # Thresholding
    # image of interest, threshold value, what value to set too if above threshold, type of threshold
    # Perform adaptive thresholding
    # filtered_bird_frame = cv2.adaptiveThreshold(resized_bird_frame, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 501, 2)


    # Create a blank image to draw contours on
    contour_image = np.zeros_like(resized_bird_frame)

    # Thresholding
    ret, thresh = cv2.threshold(resized_bird_frame, 170, 255, 0)

    # Find contours
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = contours[1:]

    cont_areas = [cv2.contourArea(cnt) for cnt in contours]
    max_contour = contours[cont_areas.index(max(cont_areas))]

    contour_image = cv2.drawContours(contour_image, max_contour, -1, (255,255,255), 3) # Or resized_bird_frame.copy() on bird

    # Plot the image with contours
    # cv2.imshow("contour", contour_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    
    # Get coordinates of all points that are =255
    point_arr = np.argwhere(contour_image == 255)

    # Create a histogram of x and y coordinates with their means marked
    com = np.mean(point_arr, axis=0)

    return resized_bird_frame, contour_image, com

def get_direction(bird_plot, com):
    """
    This function takes the bird plot and center of mass and returns the angle of the bird.
    """

    # Get the fartherst point from the center of mass
    point_arr = np.argwhere(bird_plot == 255)
    distances = np.linalg.norm(point_arr - com, axis=1)

    farthest_point = point_arr[np.argmax(distances)]

    # Get the angle of the bird
    angle = np.arctan2(abs(farthest_point[0] - com[0]), abs(farthest_point[1] - com[1])) * 180 / np.pi


    return angle, farthest_point, point_arr, distances


def display_movie(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    bird_neg = cv2.imread('test_images/bird_fake_neg.jpg', 0)

    # Check if the video file opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return
    
    angle_arr = []
    frame_num = 0
    # Read and display frames until the video ends
    while True:

        # Read a frame from the video
        ret, frame = cap.read()
        frame_num += 1

        # Check if the frame was successfully read
        if not ret:
            print("End of video.")
            break

        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        

        resized_bird_frame, bird_plot, com = get_bird(bird_neg, frame)
        bird_angle, farthest_point, point_arr, distances = get_direction(bird_plot, com)
        print(f"{frame_num} - ANGLE: {bird_angle}")

        angle_arr.append(bird_angle)


        plt.clf()

        # Plot a line from the center of mass to the farthest point
        plt.imshow(resized_bird_frame, cmap='gray')
        plt.plot([com[1], farthest_point[1]], [com[0], farthest_point[0]], c='r')

        # Plot the distance of all points =255 to the center of mass
        plt.scatter(point_arr[:, 1], point_arr[:, 0], c=distances, s=1)
        plt.scatter(com[1], com[0], c='r')
        plt.pause(.000001)





        # Break the loop if 'q' key is pressed
        if frame_num == 300:
            plt.close()
            break
    plt.close()

    print(angle_arr)
    
    for i in reversed(range(1, len(angle_arr))):
        if abs(angle_arr[i] - angle_arr[i-1]) > 5:
            angle_arr.pop(i)

    plt.plot(angle_arr)
    plt.show()
    # Release the video capture object and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()

    

# Path to the movie file
video_path = "test_images/bird_fake_mov.MOV"  # Change this to the path of your movie file

# Call the function to display the movie
display_movie(video_path)
