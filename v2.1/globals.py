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
import msvcrt
import datetime
import settings

global PARAMS
global RUNNINGVARS
global DATA 
global FRAME_CENTER
global FEED
global TOP_PLOT, CAM_PLOT, DATA_PLOT 
global SOUNDSET
global TRIALS

# USER PARAMS [CHANGE THESE]
PARAMS = settings.PARAMS

# SYTEM VARS
RUNNINGVARS = {
    # "start_time": time.time(),
    # "last_stable_time": None,
    # "override": False,
    # "running_test": False,
    "speaker_side_playing": "neither",
    # "sound_playing": "blank",
    # "sound_A_count": 0,
    # "sound_B_count": 0,
    # "control_count": 0,
    "frame_num": 0,
    # "sound_frame": 0,
    "cur_angle": 0,
    # "threads": [],
    # "thread_index": 0,
    "pause": True,
    "cam_center": (0, 0),
    # "bird_dir": None,
}

# Dataframe to store data
DATA = pd.DataFrame()

# Set up camera feed
class Feed:
    def __init__(self, FRAME_SIZE):
        self.frame_size = FRAME_SIZE
        self.feed = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        [self.feed.read(0) for i in range(2)] # Remove first two frames
        RUNNINGVARS["cam_center"] = (FRAME_SIZE// 2, FRAME_SIZE//2)

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

FEED = Feed(450) # FRAME_SIZE = 450

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
control = pygame.mixer.Sound(PARAMS["control_sound_path"])
for sound_index in range(len(PARAMS["sound_names"])):
    name = PARAMS["sound_names"][sound_index]
    path = PARAMS["sound_paths"][sound_index]
    SOUNDSET[name] = pygame.mixer.Sound(path)

pygame.mixer.Channel(0).set_volume(1.0, 0.0) # Full volume on left, mute on right
pygame.mixer.Channel(1).set_volume(0.0, 1.0) # Mute on left, full volume on right

def build_sound_sequence(SOUNDSET, min_control_spacer, seq_length):
    if seq_length < (len(SOUNDSET) + 1) * min_control_spacer + len(SOUNDSET):
        raise ValueError("seq_length too small for desired min_control_spacer")

    control_sound = ("control", control)
    
    # Start with the initial control sounds
    sound_seq = [control_sound] * min_control_spacer
    
    other_sounds = [name for name in SOUNDSET if name != "control"]

    # Add each sound with control sounds in between
    for sound_name in other_sounds:
        sound_seq.append((sound_name, SOUNDSET[sound_name]))
        sound_seq.extend([control_sound] * min_control_spacer)

    # If we still need to add control sounds to reach the sequence length
    while len(sound_seq) < seq_length:
        ran_insert = random.randint(0, len(sound_seq))
        sound_seq.insert(ran_insert, control_sound)

    return sound_seq  # Ensure we return exactly seq_length sounds


TRIALS = []
for trial_num in range(PARAMS["num_trials"]):   
    sound_sequence = build_sound_sequence(SOUNDSET, PARAMS["min_control_spacer"], PARAMS["seq_length"])
    TRIALS.append(sound_sequence)

print(TRIALS)

## TEST REMOVE LATER
# first = SOUNDSET[list(SOUNDSET.keys())[0]]
# print(first.get_length())
# first.play()
# pygame.time.delay(int(first.get_length() * 1000))


# Create a figure with two subplots and top section
fig = plt.figure(figsize=(15, 8))
gs = gridspec.GridSpec(2, 2, width_ratios=[3, 4], height_ratios=[1, 10])  # Adjust width ratios for side-by-side plots
TOP_PLOT = fig.add_subplot(gs[0, :])  # Top plot for general info
CAM_PLOT = fig.add_subplot(gs[1, 0])  # Camera plot on the left
DATA_PLOT = fig.add_subplot(gs[1, 1])  # Data plot on the right

plt.tight_layout(pad=3)
plt.ion()

def write2plot(text):
    TOP_PLOT.clear()
    TOP_PLOT.axis("off")
    TOP_PLOT.text(0.5, 0.5, text, fontsize=20, ha="center", va="center")

def on_click(event):
    if event.inaxes:
        print(f'data coords {event.xdata} {event.ydata},',
            f'pixel coords {event.x} {event.y}')
        
        RUNNINGVARS["cam_center"] = (int(event.xdata), int(event.ydata))
    
plt.connect('button_press_event', on_click)

def set_data_plots():
    pass

set_data_plots()


print("Globals Loaded")