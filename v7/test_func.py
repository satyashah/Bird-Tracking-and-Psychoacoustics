import wave
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import math

from pydub import AudioSegment
from pydub.playback import play
from multiprocessing import Process
import time

import pandas as pd
from tabulate import tabulate

import pygame

import time
import os
import datetime
import msvcrt

import random
import time
from scipy.stats import norm



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
def set_up_sound(sound_A_path, sound_B_path):
    pygame.init()
    pygame.mixer.init(channels=2)

    sound_set = {}

    sound_A_names = sound_A_path.split("/")[-1].split(".")[0] 
    sound_set[sound_A_names] = pygame.mixer.Sound(sound_A_path)

    sound_B_names = sound_B_path.split("/")[-1].split(".")[0]
    sound_set[sound_B_names] = pygame.mixer.Sound(sound_B_path)

    pygame.mixer.Channel(0).set_volume(1.0, 0.0) # Full volume on left, mute on right
    pygame.mixer.Channel(1).set_volume(0.0, 1.0) # Mute on left, full volume on right

    return sound_set

def play_sound(sound, speaker, sound_duration, event, data_collection_duration, summarize_event):

    pygame.mixer.stop()
    if speaker == "left":
        pygame.mixer.Channel(0).play(sound, loops=-1)
    elif speaker == "right":
        pygame.mixer.Channel(1).play(sound, loops=-1)
    else:
        assert False, "Invalid speaker"
    
    pygame.mixer.Channel(0).set_volume(1.0, 0.0) # Full volume on left, mute on right
    pygame.mixer.Channel(1).set_volume(0.0, 1.0) # Mute on left, full volume on right

    pygame.time.set_timer(event, sound_duration, loops=1)
    pygame.time.set_timer(summarize_event, data_collection_duration, loops=1)

    return

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
            angle_deg = -(90 - get_abs_angle(dy, dx))
        else:
            angle_deg = -(90 + get_abs_angle(dy, dx))
    else:
        if dy <= 0:
            angle_deg = -(get_abs_angle(dy, dx) - 90)
        else:
            angle_deg = -(-(get_abs_angle(dy, dx) + 90))
    
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
        
# Function to plot bird
def plot_bird(cropped_frame, beak_center, angle, frame_size, ax):
    ax.clear()
    ax.imshow(cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB), cmap='gray')
    ax.scatter(frame_size//2, frame_size//2, c='r')

    if not math.isnan(angle):
        ax.plot([frame_size//2, beak_center[0]], [frame_size//2, beak_center[1]], c='r')
        ax.scatter(beak_center[0], beak_center[1], c='r')
        ax.text(280, 50, f'Ang: {angle:.2f}\nX: {beak_center[0] - frame_size//2:.2f}', color='black', fontsize=12, backgroundcolor='white')
    
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
    mean_angle = round(last_sound_df['angle'].mean(),2)
    std_angle = round(last_sound_df['angle'].std(),2)

    # Calculate mean and std for the 'X' column
    mean_X = round(last_sound_df['X'].mean(),2)
    std_X = round(last_sound_df['X'].std(),2)

    # Calculate mean and std for the 'Y' column
    mean_Y = round(last_sound_df['Y'].mean(),2)
    std_Y = round(last_sound_df['Y'].std(),2)

    start_time = last_sound_df['time'].iloc[0]
    end_time = last_sound_df['time'].iloc[-1]


    print(tabulate([
        ['Mean angle', (f"{mean_angle} +/- {std_angle}")], 
        ['Mean X', (f"{mean_X} +/- {std_X}") ], 
        ['Time', f"{start_time} - {end_time}"]
    ], headers=['', sound_name], tablefmt='grid'))

    return mean_angle, std_angle, mean_X, std_X

def plot_mean(sound_set, data_dict, last_data_point, axs):

    df = pd.DataFrame(data_dict).T
    resolution = 90

    if last_data_point["sound"] == list(sound_set.keys())[0]:
        axs[0].set_title(list(sound_set.keys())[0])
        axs[0].set_ylim([-resolution, resolution])
        axs[0].plot(last_data_point["sound_index"], last_data_point["angle"], marker='o', markersize=2, color='blue', label='Added Point')

    
    elif last_data_point["sound"] == list(sound_set.keys())[1]:
        axs[1].set_title(list(sound_set.keys())[1])
        axs[1].set_ylim([-resolution, resolution])
        axs[1].plot(last_data_point["sound_index"], last_data_point["angle"], marker='o', markersize=2, color='orange', label='Added Point')
    

    elif len(df) > 2 and df.iloc[-2]["sound"] != last_data_point["sound"]:
        if df.iloc[-2]["sound"] == list(sound_set.keys())[0]:
            axs[0].clear()
            axs[0].set_title(list(sound_set.keys())[0])
            axs[0].set_ylim([-resolution, resolution])
            filtered_df = df[df['sound'] == list(sound_set.keys())[0]]
            if len(filtered_df) > 1:
                average_values = filtered_df.groupby(filtered_df.sound_index)["angle"].mean().iloc[:-3] # Remove last 3 for accuracy
                axs[0].set_xlim([0, len(average_values)])
                axs[0].plot(average_values.index, average_values.values, marker='o', markersize=2, color='purple', label='Average Angle')
                axs[0].axhline(y=sum(average_values.values)/len(average_values.values), color='black', linestyle='--')
        else:
            axs[1].clear()
            axs[1].set_title(list(sound_set.keys())[1])
            axs[1].set_ylim([-resolution, resolution])
            filtered_df = df[df['sound'] == list(sound_set.keys())[1]]
            if len(filtered_df) > 1:
                average_values = filtered_df.groupby(filtered_df.sound_index)["angle"].mean().iloc[:-3]
                axs[1].set_xlim([0, len(average_values)])
                axs[1].plot(average_values.index, average_values.values, marker='o', markersize=2, color='red', label='Average Angle')
                axs[1].axhline(y=sum(average_values.values)/len(average_values.values), color='black', linestyle='--')
    
    return

def plot_final(data_dict, sound_set):
    fig = plt.figure(figsize=(15, 8))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1,1]) # Create a grid with 2 rows and 1 column

    ax_top = fig.add_subplot(gs[0, 0]) # Add the first subplot to the first row
    ax_bottom = fig.add_subplot(gs[1, 0]) # Add the second subplot to the second row
    
    df = pd.DataFrame(data_dict).T
    axs = [ax_top, ax_bottom]

    axs[0].clear()
    axs[0].set_title(list(sound_set.keys())[0])
    axs[0].set_ylim([-120, 120])
    filtered_df = df[df['sound'] == list(sound_set.keys())[0]]
    if len(filtered_df) > 1:
        average_values = filtered_df.groupby(filtered_df.sound_index)["angle"].mean().iloc[:-3] # Remove last 3 for accuracy
        axs[0].set_xlim([0, len(average_values)])
        axs[0].plot(average_values.index, average_values.values, marker='o', markersize=2, color='purple', label='Average Angle')
        axs[0].axhline(y=sum(average_values.values)/len(average_values.values), color='black', linestyle='--')

    axs[1].clear()
    axs[1].set_title(list(sound_set.keys())[1])
    axs[1].set_ylim([-120, 120])
    filtered_df = df[df['sound'] == list(sound_set.keys())[1]]
    if len(filtered_df) > 1:
        average_values = filtered_df.groupby(filtered_df.sound_index)["angle"].mean().iloc[:-3]
        axs[1].set_xlim([0, len(average_values)])
        axs[1].plot(average_values.index, average_values.values, marker='o', markersize=2, color='red', label='Average Angle')
        axs[1].axhline(y=sum(average_values.values)/len(average_values.values), color='black', linestyle='--')

    plt.show()

# Other
clear_terminal = lambda: os.system('cls')

