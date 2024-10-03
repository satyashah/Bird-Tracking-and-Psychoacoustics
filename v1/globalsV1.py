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
global TOP_PLOT, CAM_PLOT, DATA_PLOT_TOP, DATA_PLOT_BOTTOM 
global SOUNDSET
global STOP_SOUND_EVENT, SUMMARIZE_EVENT, RESUME_EVENT
global DATA_BUS

# USER PARAMS [CHANGE THESE]
PARAMS = settings.PARAMS

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
    "control_count": 0,
    "frame_num": 0,
    "sound_frame": 0,
    "cur_angle": 0,
    "threads": [],
    "thread_index": 0,
    "pause": True,
    "cam_center": (0, 0),
    "bird_dir": None,
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

sound_A_name = PARAMS["sound_A_name"]
SOUNDSET[sound_A_name] = [pygame.mixer.Sound(path) for path in PARAMS["sound_A_paths"]]

sound_B_name = PARAMS["sound_B_name"]
SOUNDSET[sound_B_name] = [pygame.mixer.Sound(path) for path in PARAMS["sound_B_paths"]]

pygame.mixer.Channel(0).set_volume(1.0, 0.0) # Full volume on left, mute on right
pygame.mixer.Channel(1).set_volume(0.0, 1.0) # Mute on left, full volume on right


# Create a figure with two subplots and top section
# plt.style.use("dark_background")
fig = plt.figure(figsize=(15, 8))
gs = gridspec.GridSpec(4, 2, width_ratios=[2, 2], height_ratios=[1, 6, 6, 6])
TOP_PLOT = fig.add_subplot(gs[0, :])
CAM_PLOT = fig.add_subplot(gs[1:4, 0])
DATA_PLOT_TOP = fig.add_subplot(gs[1, 1])
DATA_PLOT_BOTTOM = fig.add_subplot(gs[2, 1])
DATA_PLOT_CONTROL = fig.add_subplot(gs[3, 1])
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
    
    if RUNNINGVARS["sound_playing"] == "blank" or RUNNINGVARS["sound_playing"] == "control":
        DATA_PLOT_CONTROL.clear()
        DATA_PLOT_CONTROL.set_title(f"Control Sound ({RUNNINGVARS['control_count']})")
        DATA_PLOT_CONTROL.set_xlabel('Time (ms)')
        DATA_PLOT_CONTROL.set_ylabel('Mean Angle')
        DATA_PLOT_CONTROL.set_ylim([-PARAMS["resolution"], PARAMS["resolution"]])
        DATA_PLOT_CONTROL.set_xlim([0, PARAMS["data_collection_duration"]])

set_data_plots()


# EVENTS
STOP_SOUND_EVENT = pygame.USEREVENT + 1
GET_POINT_EVENT = pygame.USEREVENT + 2
SUMMARIZE_EVENT = pygame.USEREVENT + 3
RESUME_EVENT = pygame.USEREVENT + 4


# Threading
DATA_BUS = Queue()

print("Globals Loaded")