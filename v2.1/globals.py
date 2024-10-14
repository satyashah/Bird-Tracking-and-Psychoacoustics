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

# SYSTEM VARS
RUNNINGVARS = {
    "start_time": time.time(),
    "running_test": False,
    "speaker_side_playing": "neither",
    "sound_playing": "blank",
    "trial_num": 0,
    "stim_num": -1,
    "cur_angle": 0,
    "pause": True,
    "cam_center": (0, 0),
}

# Dataframe to store data
DATA = pd.DataFrame()

# Set up camera feed
class Feed:
    def __init__(self, FRAME_SIZE):
        self.frame_size = FRAME_SIZE
        self.feed = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        [self.feed.read(0) for _ in range(2)]  # Remove first two frames
        RUNNINGVARS["cam_center"] = (FRAME_SIZE // 2, FRAME_SIZE // 2)

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

FEED = Feed(450)  # FRAME_SIZE = 450

# Camera Center Set Up
FRAME_CENTER = (328, 262)  # Set manually or use set_up_cam()

# Sound Set Up
pygame.init()
pygame.mixer.init(channels=2)

SOUNDSET = {}
control = pygame.mixer.Sound(PARAMS["control_sound_path"])
for sound_index in range(len(PARAMS["sound_names"])):
    name = PARAMS["sound_names"][sound_index]
    path = PARAMS["sound_paths"][sound_index]
    SOUNDSET[name] = pygame.mixer.Sound(path)

pygame.mixer.Channel(0).set_volume(1.0, 0.0)  # Full volume on left, mute on right
pygame.mixer.Channel(1).set_volume(0.0, 1.0)  # Mute on left, full volume on right

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

# Create a figure with two subplots and top section
fig = plt.figure(figsize=(10, 6))
gs = gridspec.GridSpec(2, 2, width_ratios=[3, 4], height_ratios=[1, 10])
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
        RUNNINGVARS["cam_center"] = (int(event.xdata), int(event.ydata))

plt.connect('button_press_event', on_click)

def set_data_plots():
    categories = ['control'] + PARAMS["sound_names"]
    y_values = [[0] for _ in categories]  # Initialize y_values with a list of lists, one for each category
    
    DATA_PLOT.clear()
    box = DATA_PLOT.boxplot(y_values, labels=categories)

    for element in ['boxes', 'whiskers', 'fliers', 'medians', 'caps']:
        plt.setp(box[element], color='none')

    DATA_PLOT.set_ylim(-145, 145)
    DATA_PLOT.set_ylabel('Movement (degrees)')
    DATA_PLOT.set_title('Movement Per Sound')

set_data_plots()

# EVENTS
STOP_SOUND_EVENT = pygame.USEREVENT + 1
GET_POINT_EVENT = pygame.USEREVENT + 2
SUMMARIZE_EVENT = pygame.USEREVENT + 3
RESUME_EVENT = pygame.USEREVENT + 4

# Threading
DATA_BUS = Queue()
print("Globals Loaded")
