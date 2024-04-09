"""
Application Description:
    TBD
"""
from func import *
import keyboard
import pygame
import pandas as pd
import datetime


# # Params
center_cords = (332, 250)
FRAME_SIZE = 400

sound_tone_path = "test_sounds/3kHz.wav"
canary_sound_path = "test_sounds/ZFAB.wav"

duration_milli_sec = 10000

data_file_name = "canary_3khz"

# Setup Sound

sound_left, sound_right = set_up_sound(sound_tone_path, canary_sound_path)




# Application

tone_playing = False
sound_playing = False
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

print(f"Application started... {timestamp}")
# Live Feed
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("Error: Could not open video.") if not cap.isOpened() else None
ret, frame = cap.read(0) # Remove first frame

frame_num = 0
data_dict = {}
start_time = time.time()

while True:
    frame_num += 1
    
    try:
        cropped_frame, angle, beak_center = display_camara(cap, center_cords, FRAME_SIZE)
        plot_bird(cropped_frame, beak_center, angle, FRAME_SIZE)
    except Exception as e:
        print(f"Error: {e}")
        continue

    # Save Data
    data_dict[frame_num] = {}
    data_dict[frame_num]["time"] = round(time.time() - start_time,2)
    data_dict[frame_num]["angle"] = round(angle,2)
    data_dict[frame_num]["tone"] = tone_playing
    data_dict[frame_num]["sound"] = sound_playing

    if keyboard.is_pressed('1'):
        if not tone_playing:
            pygame.mixer.Channel(1).stop()
            print(f"Tone Starting...")
            pygame.mixer.Channel(0).play(sound_left, loops=-1)
            tone_playing = True
            sound_playing = False
    
    if keyboard.is_pressed('2'):
        if not sound_playing:
            pygame.mixer.Channel(0).stop()
            print(f"Sound Starting...")
            pygame.mixer.Channel(1).play(sound_right, loops=-1)
            sound_playing = True
            tone_playing = False
            time.sleep(1)
    
    if keyboard.is_pressed('0'):
        print("Resetting...")
        if tone_playing:
            pygame.mixer.Channel(0).stop()
        if sound_playing:
            pygame.mixer.Channel(1).stop()
        
        tone_playing = False
        sound_playing = False

    if keyboard.is_pressed('9'):
        print("Exiting...")
        if tone_playing:
            pygame.mixer.Channel(0).stop()
        if sound_playing:
            pygame.mixer.Channel(1).stop()
        
        break
    
        
# Save Data
df = pd.DataFrame(data_dict).T
df.to_csv(f"data/{data_file_name}_{timestamp}.csv", index=False)
print(df)