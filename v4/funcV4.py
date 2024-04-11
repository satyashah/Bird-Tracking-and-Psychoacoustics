import wave
import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

from pydub import AudioSegment
from pydub.playback import play
from multiprocessing import Process
import time

import pandas as pd
from tabulate import tabulate

import pygame

import time


# Set Up Camera
def set_up_cam():
    # Live Feed
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print("Error: Could not open video") if not cap.isOpened() else None
    ret, frame = cap.read(0) # Remove first frame
    ret, frame = cap.read(0) # Remove first frame

    clicked_coordinates = []  # List to store clicked coordinates

    def onclick(event):
        if event.inaxes is not None:
            print('Selected Bird Center ({:.2f}, {:.2f})'.format(int(event.xdata), int(event.ydata)))
            clicked_coordinates.append((int(event.xdata), int(event.ydata)))  # Append clicked coordinates
            plt.close()

    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), cmap='gray')
    plt.title('Click on the Center of Bird')

    plt.gcf().canvas.mpl_connect('button_press_event', onclick)
    plt.show()

    # Wait for user to click
    plt.pause(0.1)

    # This return is executed after the user clicks and the plot is closed
    return clicked_coordinates[-1]  # Return the last clicked coordinates

# Sound
def set_up_sound(tone_sound_path, test_sound_paths):
    pygame.init()
    pygame.mixer.init(channels=2)

    tone = pygame.mixer.Sound(tone_sound_path)

    soundArr = []
    for sound_path in test_sound_paths:
        soundArr.append(pygame.mixer.Sound(sound_path))

    pygame.mixer.Channel(0).set_volume(1.0, 0.0) # Full volume on left, mute on right
    pygame.mixer.Channel(1).set_volume(0.0, 1.0) # Mute on left, full volume on right

    return tone, soundArr

def play_sound(sound, speaker):

    pygame.mixer.stop()
    if speaker == "left":
        pygame.mixer.Channel(0).play(sound, loops=-1)
    elif speaker == "right":
        pygame.mixer.Channel(1).play(sound, loops=-1)
    else:
        assert False, "Invalid speaker"
    
    pygame.mixer.Channel(0).set_volume(1.0, 0.0) # Full volume on left, mute on right
    pygame.mixer.Channel(1).set_volume(0.0, 1.0) # Mute on left, full volume on right

    pygame.time.set_timer(pygame.USEREVENT, 500)
    return

def create_sound_set(tone_sound_path, test_sound_paths):
    # Dictionary to store sound paths
    sound_set = []
    
    # Remove directory path and file extension for tone sound path
    tone_sound = tone_sound_path.split("/")[-1].split(".")[0]
    sound_set.append(f"tone_{tone_sound}")
    
    # Remove directory path and file extension for each test sound path
    test_sounds = [path.split("/")[-1].split(".")[0] for path in test_sound_paths]
    for sound in test_sounds:
        sound_set.append(f"{sound}")
    
    return sound_set

# Frame
def crop(FRAME_SIZE, CENTER, frame):
    """
    This function takes an image and returns a cropped version of the image.
    """

    # Calculate crop boundaries
    crop_x1 = max(0, CENTER[0] - FRAME_SIZE // 2)
    crop_x2 = min(frame.shape[1], CENTER[0] + FRAME_SIZE // 2)
    crop_y1 = max(0, CENTER[1] - FRAME_SIZE // 2)
    crop_y2 = min(frame.shape[0], CENTER[1] + FRAME_SIZE // 2)

    cropped_frame = frame[crop_y1:crop_y2, crop_x1:crop_x2]

    return cropped_frame

def get_beak_center(frame):
    """
    This function takes an image and returns the center of the beak.
    """
    # Define BGR range for the color red
    lower_red_bgr = np.array([0, 0, 70])   # Lower bound of red (in BGR format)
    upper_red_bgr = np.array([10, 10, 100])  # Upper bound of red (in BGR format)

    # Create a mask for red pixels
    mask = cv2.inRange(frame, lower_red_bgr, upper_red_bgr)

    # Apply the mask to extract red pixels
    red_pixels = cv2.bitwise_and(frame, frame, mask=mask)

    # Find the median x and y coordinates of the red pixels that are not 0
    red_indices = np.where(mask != 0)
    if len(red_indices[0]) != 0:
        median_x = np.median(red_indices[1])  # Median of non-zero x coordinates
        median_y = np.median(red_indices[0])  # Median of non-zero y coordinates
    else:
        median_x =  np.nan
        median_y = np.nan

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

# Feed
def display_camara(cap, center_cords, FRAME_SIZE):
    # # Read and display next frame

    # Read a frame from the video
    ret, frame = cap.read(0)

    # Check if the frame was successfully read
    if not ret:
        print("Error")
        return

    # Crop the frame
    cropped_frame = crop(FRAME_SIZE, center_cords, frame)

    # Get the center of the beak
    beak_center_x, beak_center_y, red_indices = get_beak_center(cropped_frame)

    # Get the Angle of the beak
    angle = calculate_angle((FRAME_SIZE//2, FRAME_SIZE//2), (beak_center_x, beak_center_y))

    
    return cropped_frame, angle, (beak_center_x, beak_center_y)
        
def plot_bird(cropped_frame, beak_center, angle, frame_size):
    plt.clf()
    plt.imshow(cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB), cmap='gray')
    plt.scatter(frame_size//2, frame_size//2, c='r')
    # plt.scatter(red_indices[1], red_indices[0], s=1)

    if not math.isnan(angle):
        plt.plot([frame_size//2, beak_center[0]], [frame_size//2, beak_center[1]], c='r')
        plt.scatter(beak_center[0], beak_center[1], c='r')
        plt.text(beak_center[0]+20, beak_center[1]-20, f'{angle:.2f}', color='black', fontsize=12, backgroundcolor='white')

    plt.pause(.00000001)


# Data
def summarize_data(data_dict, sound_name):
    df = pd.DataFrame(data_dict).T

    df['group'] = (df['sound'] != df['sound'].shift()).cumsum()

    # Get the last sound
    last_sound = df['sound'].iloc[-1]

    # Get the last group number for the sound of interest
    last_group_number = df.loc[df['sound'] == last_sound, 'group'].max()
    # Filter the DataFrame to get only the rows corresponding to the last group of the sound of interest
    last_sound_df = df[df['group'] == last_group_number]

    # Calculate mean and std for the 'time' column
    mean_angle = last_sound_df['angle'].mean()
    std_angle = last_sound_df['angle'].std()

    start_time = last_sound_df['time'].iloc[0]
    end_time = last_sound_df['time'].iloc[-1]


    print(tabulate([['Mean angle', mean_angle], ['Std deviation', std_angle], ['Time', str(start_time) + "-" + str(end_time)]], headers=['', sound_name], tablefmt='grid'))