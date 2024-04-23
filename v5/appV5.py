from funcV5 import *

# User Params [CHANGE THESE]
FRAME_SIZE = 200

left_sound_paths = ["test_sounds/ABCD_perry.wav", "test_sounds/CanaryAB.wav", "test_sounds/pu995_ABCDEFG.wav"] #
right_sound_paths = ["test_sounds/ABCD_perry.wav", "test_sounds/CanaryAB.wav", "test_sounds/pu995_ABCDEFG.wav"]

sound_duration = 1000
data_collection_duration = 3000 # note this starts at beginning of sound


# System Params [DO NOT CHANGE]
clear_terminal()

x,y = set_up_cam()
center_cords = (x, y)

data_file_name = "test_data"

STOP_SOUND_EVENT = pygame.USEREVENT + 1
SUMMARIZE_EVENT = pygame.USEREVENT + 2

frame_num = 0
data_dict = {}
start_time = time.time()
sound_playing = "Blank"

# Setup Sound
assert len(left_sound_paths) <= 3 or len(right_sound_paths) <= 3, "Error: Too many test sounds. Max 7 allowed"
sound_arr = set_up_sound(left_sound_paths, right_sound_paths)

sound_names = create_sound_set(left_sound_paths, right_sound_paths)
print("Sound Loaded:",sound_names)


# Application
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
print(f"Application started... {timestamp}")

# Live Feed
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
ret, frame = cap.read(0) # Remove first frame

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
    data_dict[frame_num]["X"] = beak_center[0] - FRAME_SIZE//2
    data_dict[frame_num]["Y"] = beak_center[1] - FRAME_SIZE//2
    data_dict[frame_num]["sound"] = sound_playing


    for event in pygame.event.get():
        if event.type == STOP_SOUND_EVENT:
            pygame.mixer.stop()

        if event.type == SUMMARIZE_EVENT:
            summarize_data(data_dict, sound_playing)
            sound_playing = "Blank"
    
    if msvcrt.kbhit():  # Check if a key has been pressed
        clear_terminal()
        key = msvcrt.getch()
        if key.isdigit():
            key_num = int(key)
        
            if key_num == 0:
                print("\nExiting...\n")
                pygame.mixer.stop()
                break
            else:
                if key_num == 1 or key_num == 4 or key_num == 7:
                    speaker_side = "left"
                    arr_loc = key_num//3
                elif key_num == 2 or key_num == 5 or key_num == 8:
                    speaker_side = "right"
                    arr_loc = (key_num-1)//3 + 3
                else:
                    assert False, "Error: Invalid key pressed"

                if sound_playing == sound_names[arr_loc]:
                    data_dict[frame_num] = {'time': round(time.time() - start_time,2), 'angle': round(angle,2), 'X': beak_center[0] - FRAME_SIZE//2, 'Y': beak_center[1] - FRAME_SIZE//2, 'sound': "None"}
                    frame_num += 1

                print(f"\n{sound_names[arr_loc]} Starting on {speaker_side} Speaker...\n")
                print(f"Initial \n\tAngle => {round(angle,2)} \n\tX => {beak_center[0] - FRAME_SIZE//2}\n")
                play_sound(sound_arr[arr_loc], speaker_side, sound_duration, STOP_SOUND_EVENT, data_collection_duration, SUMMARIZE_EVENT)
                sound_playing = sound_names[arr_loc]
            
            key = -1

    #time.sleep(0.1)

plt.close()
    

        
# Save Data
df = pd.DataFrame(data_dict).T
df.to_csv(f"data/{data_file_name}_{timestamp}.csv", index=False)

# Calculate mean and standard deviation for each sound group
sound_stats = df.groupby('sound').agg({'angle': ['mean', 'std'], 'X': ['mean', 'std']})
# Rename columns for clarity
sound_stats.columns = ['mean_angle', 'std_dev_angle', 'mean_X', 'std_dev_X']
print(sound_stats)

get_time_plots(df)
plot_summarized_data(sound_stats)

