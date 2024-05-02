import pandas as pd
import cv2
import matplotlib.pyplot as plt
import os
from matplotlib import gridspec
import numpy as np
import math
import time
import pygame
import random


global PARAMS
global DATA 
global FRAME_CENTER
global FEED
global TOP_PLOT, CAM_PLOT, DATA_PLOT_TOP, DATA_PLOT_BOTTOM 
global SOUNDSET


# Dictionary to running parameters
PARAMS = {
    "sound_A_path": "test_sounds/ABCD_perry.wav",
    "sound_B_path": "test_sounds/ZFAB.wav",

    "bird_dir": None,

    "stable_threshold": 25, # Bird must be within +/- this angle to be considered stable
    "stable_duration": 500, # Time in milliseconds to be considered stable before starting test

    "switch_thresh": 145, # Angle threshold to switch direction of calculate angle
}


RUNNINGVARS = {
    "last_stable_time": None,
    "override": False,
    "running_test": False,
    "speaker_side_playing": "neither",
    "sound_playing": "blank",
    "sound_A_count": 0,
    "sound_B_count": 0,
}

# Dataframe to store data
columns = ['time', 'sound_index', 'angle', 'X', 'Y', 'sound', 'side']
DATA = pd.DataFrame(columns=columns)

# Set up camera feed
class Feed:
    def __init__(self, FRAME_SIZE):
        self.frame_size = FRAME_SIZE
        self.feed = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        [self.feed.read(0) for i in range(2)] # Remove first two frames

    def get_frame(self):
        _, frame = self.feed.read()
        return frame
    
    def get_cropped_frame(self):
        assert FRAME_CENTER is not None, "Frame Center is not set"
        frame = self.get_frame()
        half_size = self.frame_size // 2
        crop_x1 = max(0, FRAME_CENTER[0] - half_size)
        crop_x2 = min(frame.shape[1], FRAME_CENTER[0] + half_size)
        crop_y1 = max(0, FRAME_CENTER[1] - half_size)
        crop_y2 = min(frame.shape[0], FRAME_CENTER[1] + half_size)

        # Crop the frame using NumPy slicing
        cropped_frame = frame[crop_y1:crop_y2, crop_x1:crop_x2]

        return cropped_frame
FEED = Feed(400) # FRAME_SIZE = 400

# Camara and Frame Center Set Up
def set_up_cam():
    frame = FEED.get_frame()
    
    clicked_coordinates = []  # List to store clicked coordinates

    def onclick(event):
        if event.inaxes is not None:
            print(f'Selected Bird Center: ({int(event.xdata)}, {int(event.ydata)})')
            clicked_coordinates.append((int(event.xdata), int(event.ydata)))  # Append clicked coordinates
            plt.close()

    plt.title('Click on the Center of Bird')
    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), cmap='gray')
    plt.gcf().canvas.mpl_connect('button_press_event', onclick)
    plt.show() # Show the plot, wait for the user to click

    # This return is executed after the user clicks and the plot is closed
    return clicked_coordinates[-1][0], clicked_coordinates[-1][1] # Return the last clicked coordinates
FRAME_CENTER = (333, 254) #set_up_cam()


# Create a figure with two subplots and top section
fig = plt.figure(figsize=(15, 8))
gs = gridspec.GridSpec(3, 2, width_ratios=[2, 2], height_ratios=[1, 6, 6])
TOP_PLOT = fig.add_subplot(gs[0, :])
TOP_PLOT.clear()
TOP_PLOT.axis("off")
CAM_PLOT = fig.add_subplot(gs[1:3, 0])
DATA_PLOT_TOP = fig.add_subplot(gs[1, 1])
DATA_PLOT_BOTTOM = fig.add_subplot(gs[2, 1])
plt.tight_layout(pad=3)


# Sound Set Up
pygame.init()
pygame.mixer.init(channels=2)

SOUNDSET = {}

sound_A_names = PARAMS["sound_A_path"].split("/")[-1].split(".")[0] 
SOUNDSET[sound_A_names] = pygame.mixer.Sound(PARAMS["sound_A_path"])

sound_B_names = PARAMS["sound_B_path"].split("/")[-1].split(".")[0]
SOUNDSET[sound_B_names] = pygame.mixer.Sound(PARAMS["sound_B_path"])

pygame.mixer.Channel(0).set_volume(1.0, 0.0) # Full volume on left, mute on right
pygame.mixer.Channel(1).set_volume(0.0, 1.0) # Mute on left, full volume on right

print("Globals Loaded")