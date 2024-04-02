import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

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

def get_beak_center(img):
    """
    This function takes an image and returns the center of the beak.
    """
    # Define BGR range for the color red
    lower_red_bgr = np.array([0, 0, 70])   # Lower bound of red (in BGR format)
    upper_red_bgr = np.array([10, 10, 100])  # Upper bound of red (in BGR format)

    # Create a mask for red pixels
    mask = cv2.inRange(img, lower_red_bgr, upper_red_bgr)

    # Apply the mask to extract red pixels
    red_pixels = cv2.bitwise_and(img, img, mask=mask)

    # Find the median x and y coordinates of the red pixels that are not 0
    red_indices = np.where(mask != 0)
    median_x = np.median(red_indices[1])  # Median of non-zero x coordinates
    median_y = np.median(red_indices[0])  # Median of non-zero y coordinates

    return median_x, median_y, red_indices

def calculate_angle(center, point):
    dx = point[0] - center[0]
    dy = -(point[1] - center[1])  # Since y axis is flipped


    def get_abs_angle(dy, dx):
        dy = abs(dy)
        dx = abs(dx)
        # Calculate the angle in radians
        angle_rad = np.arctan2(dy, dx)
        
        # Convert radians to degrees
        angle_deg = np.degrees(angle_rad)

        return angle_deg

    if dx <= 0:
        if dy <= 0:
            angle_deg = 90 - get_abs_angle(dy, dx)
        else:
            angle_deg = 90 + get_abs_angle(dy, dx)
    else:
        if dy <= 0:
            angle_deg = get_abs_angle(dy, dx) - 90
        else:
            angle_deg = -(get_abs_angle(dy, dx) + 90)
    
    return angle_deg

def display_movie(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video file opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return
    
    frame_num = 0
    movement = []
    # Read and display frames until the video ends
    while True:

        # Read a frame from the video
        ret, frame = cap.read(0)
        frame_num += 1

        # Check if the frame was successfully read
        if not ret:
            print("End of video.")
            break

        
        # Crop the frame
        FRAME_SIZE = 600
        
        # Crop the frame
        cropped_frame = crop(FRAME_SIZE, FRAME_SIZE, 30, -80, frame)

        # Get the center of the beak
        beak_center_x, beak_center_y, red_indices = get_beak_center(cropped_frame)

        # Get the Angle of the beak
        angle = calculate_angle((FRAME_SIZE//2, FRAME_SIZE//2), (beak_center_x, beak_center_y))
        movement.append(angle)
        

        # Display the frame
        plt.clf()
        plt.imshow(cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB), cmap='gray')
        # plt.plot([FRAME_SIZE//2, beak_center_x], [FRAME_SIZE//2, beak_center_y], c='r')
        # plt.scatter(red_indices[1], red_indices[0], s=1)
        # plt.scatter(FRAME_SIZE//2, FRAME_SIZE//2, c='r')

        plt.scatter(beak_center_x, beak_center_y, c='r')
        plt.text(beak_center_x+20, beak_center_y-20, f'{angle:.2f}', color='black', fontsize=12, backgroundcolor='white')
        plt.pause(.00000001)

    plt.close()

    # Print some statistics
    print("Mean Angle: ", np.mean(movement))
    print("Standard Deviation: ", np.std(movement))
    print("Max Angle: ", np.max(movement))
    print("Min Angle: ", np.min(movement))

    # Plot the movement
    plt.plot(movement)
    plt.show()


# Path to the movie file
video_path = "test_content/bird_v1_clip.mp4"  # Change this to the path of your movie file

# Call the function to display the movie
display_movie(video_path)
