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
import threading
from queue import Queue


global PARAMS
global RUNNINGVARS
global DATA 
global FRAME_CENTER
global FEED
global TOP_PLOT, CAM_PLOT, DATA_PLOT_TOP, DATA_PLOT_BOTTOM 
global SOUNDSET
global STOP_SOUND_EVENT, SUMMARIZE_EVENT, RESUME_EVENT
global DATA_BUS

# USER PARAMS
PARAMS = {
    "sound_A_path": "test_sounds/ABCD_perry.wav",
    "sound_B_path": "test_sounds/ABCDallrev_perry.wav",

    "bird_dir": None,

    "stable_threshold": 25, # Bird must be within +/- this angle to be considered stable
    "stable_duration": 500, # Time in milliseconds to be considered stable before starting test

    "switch_thresh": 145, # Angle threshold to switch direction of calculate angle
    
    "data_collection_duration": 3000, # Duration of data collection in ms
    "sound_duration": 1000, # Duration of sound in ms
    "sample_rate": 100, # Data collection per X ms
    "time_between_sounds": 3000, # Time between sounds in ms

    "resolution": 120, # Resolution of the angle plot
}

# SYTEM VARS
RUNNINGVARS = {
    "start_time": time.time(),
    "last_stable_time": None,
    "override": False,
    "running_test": False,
    "speaker_side_playing": "neither",
    "sound_playing": "blank",
    "sound_A_count": 0,
    "sound_B_count": 0,
    "frame_num": 0,
    "sound_frame": 0,
    "cur_angle": 0,
    "threads": [],
    "thread_index": 0,
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
FRAME_CENTER = set_up_cam()

# Sound Set Up
pygame.init()
pygame.mixer.init(channels=2)

SOUNDSET = {}

sound_A_name = PARAMS["sound_A_path"].split("/")[-1].split(".")[0] 
SOUNDSET[sound_A_name] = pygame.mixer.Sound(PARAMS["sound_A_path"])

sound_B_name = PARAMS["sound_B_path"].split("/")[-1].split(".")[0]
SOUNDSET[sound_B_name] = pygame.mixer.Sound(PARAMS["sound_B_path"])

pygame.mixer.Channel(0).set_volume(1.0, 0.0) # Full volume on left, mute on right
pygame.mixer.Channel(1).set_volume(0.0, 1.0) # Mute on left, full volume on right


# Create a figure with two subplots and top section
# plt.style.use("dark_background")
fig = plt.figure(figsize=(15, 8))
gs = gridspec.GridSpec(3, 2, width_ratios=[2, 2], height_ratios=[1, 6, 6])
TOP_PLOT = fig.add_subplot(gs[0, :])
CAM_PLOT = fig.add_subplot(gs[1:3, 0])
DATA_PLOT_TOP = fig.add_subplot(gs[1, 1])
DATA_PLOT_BOTTOM = fig.add_subplot(gs[2, 1])
plt.tight_layout(pad=3)
plt.ion()

TOP_PLOT.clear()
TOP_PLOT.axis("off")
TOP_PLOT.text(0.5, 0.5, f"Playing {RUNNINGVARS["sound_playing"]} from {RUNNINGVARS["speaker_side_playing"]} side", fontsize=20, ha="center", va="center")


def set_data_plots():
    if RUNNINGVARS["sound_playing"] == "blank" or RUNNINGVARS["sound_playing"] is list(SOUNDSET.keys())[0]:
        DATA_PLOT_TOP.clear()
        DATA_PLOT_TOP.set_title(f"{list(SOUNDSET.keys())[0]} ({RUNNINGVARS["sound_A_count"]})")
        DATA_PLOT_TOP.set_xlabel('Time (ms)')
        DATA_PLOT_TOP.set_ylabel('Mean Angle')
        DATA_PLOT_TOP.set_ylim([-PARAMS["resolution"], PARAMS["resolution"]])
        DATA_PLOT_TOP.set_xlim([0, PARAMS["data_collection_duration"]])

    if RUNNINGVARS["sound_playing"] == "blank" or RUNNINGVARS["sound_playing"] is list(SOUNDSET.keys())[1]:
        DATA_PLOT_BOTTOM.clear()
        DATA_PLOT_BOTTOM.set_title(f"{list(SOUNDSET.keys())[1]} ({RUNNINGVARS["sound_B_count"]})")
        DATA_PLOT_BOTTOM.set_xlabel('Time (ms)')
        DATA_PLOT_BOTTOM.set_ylabel('Mean Angle')
        DATA_PLOT_BOTTOM.set_ylim([-PARAMS["resolution"], PARAMS["resolution"]])
        DATA_PLOT_BOTTOM.set_xlim([0, PARAMS["data_collection_duration"]])  
set_data_plots()


# EVENTS
STOP_SOUND_EVENT = pygame.USEREVENT + 1
GET_POINT_EVENT = pygame.USEREVENT + 2
SUMMARIZE_EVENT = pygame.USEREVENT + 3
RESUME_EVENT = pygame.USEREVENT + 4


# Threading
DATA_BUS = Queue()

print("Globals Loaded")