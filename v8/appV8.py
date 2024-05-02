from funcV8 import *

# User Params [CHANGE THESE]
FRAME_SIZE = 400
sound_A_path = "test_sounds/ABCD_perry.wav"
sound_B_path = "test_sounds/ZFAB.wav"

sound_duration = 1000
data_collection_duration = 3000 # note this starts at beginning of sound
time_between_sounds = 5000


stable_threshold = (-20, 20, 500) # (min, max, time (ms) to be stable for)


# System Params [DO NOT CHANGE]
clear_terminal()

x,y = set_up_cam()
center_cords =  (x, y)

data_file_name = "test_data"

STOP_SOUND_EVENT = pygame.USEREVENT + 1
SUMMARIZE_EVENT = pygame.USEREVENT + 2
RESUME_EVENT = pygame.USEREVENT + 3

frame_num = 0
sound_frame = 0
data_dict = {}
start_time = time.time()
last_stable_time = time.time()
sound_playing = "Blank"
rand_side = "neither"
running_test = False
override = False
data_collection_duration = data_collection_duration + 500


# Setup Sound
sound_set = set_up_sound(sound_A_path, sound_B_path)
print("Sound Loaded:", sound_set.keys())

# Application
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
print(f"Application started... {timestamp}")

# Live Feed
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
ret, frame = cap.read(0) # Remove first frame

# Create a figure with two subplots and top section
top_info, bird_plot, data_graphs_2 = build_plot()

while True:
    
    frame_num += 1
    
    top_info.clear()
    top_info.axis("off")
    top_info.text(0.5, 0.5, f"Playing {sound_playing} from {rand_side} side", fontsize=20, ha="center", va="center")
    
    cropped_frame, angle, beak_center = display_camara(cap, center_cords, FRAME_SIZE)
    plot_bird(cropped_frame, beak_center, angle, FRAME_SIZE, bird_plot)


    # Reset the timer if the bird is not stable
    if beak_center[0] is np.nan or angle < stable_threshold[0] or angle > stable_threshold[1] or beak_center[1] - FRAME_SIZE//2 < 0:
        last_stable_time = time.time()

    # Start the test if the bird is stable and a test is not already running
    if override or (not running_test and time.time() - last_stable_time > stable_threshold[2]/1000):
        print("Bird is stable") 
        running_test = True
        override = False

        sound_keys = list(sound_set.keys())
        rand_sound = random.choices(sound_keys, weights=get_weight(sound_keys[0], sound_keys[1], data_dict))[0]
        rand_side = random.choice(["left", "right"])

        # Run code to play sound

        # If the same sound is playing, don't record the data
        if sound_playing == rand_sound:
            data_dict[frame_num] = {
                'time': round(time.time() - start_time,2), 
                'angle': round(angle,2), 
                'X': beak_center[0] - FRAME_SIZE//2, 
                'Y': beak_center[1] - FRAME_SIZE//2, 
                'sound': "None"
            }

            frame_num += 1

        sound_frame = frame_num
        print(f"\n{rand_sound} Starting on {rand_side} Speaker...\n")
        print(f"Initial \n\tAngle => {round(angle,2)} \n\tX => {beak_center[0] - FRAME_SIZE//2}\n")
        play_sound(sound_set[rand_sound], rand_side, sound_duration, STOP_SOUND_EVENT, data_collection_duration, SUMMARIZE_EVENT)
        sound_playing = rand_sound
        
    

    # Save Data
    direction_constant = -1 if rand_side == "left" else 1 # Translate L/R to Toward/Away

    data_dict[frame_num] = {}
    data_dict[frame_num]["time"] = round(time.time() - start_time,2)
    data_dict[frame_num]["sound_index"] = frame_num - sound_frame
    data_dict[frame_num]["angle"] = round(angle,2) * direction_constant
    data_dict[frame_num]["X"] = beak_center[0] - FRAME_SIZE//2
    data_dict[frame_num]["Y"] = beak_center[1] - FRAME_SIZE//2
    data_dict[frame_num]["sound"] = sound_playing
    data_dict[frame_num]["side"] = rand_side

    plot_mean(sound_set, data_dict, data_dict[frame_num], data_graphs_2, data_collection_duration)
    
    # Events to maintain the application
    for event in pygame.event.get():
        if event.type == STOP_SOUND_EVENT:
            print("Stopping sound")
            pygame.mixer.stop()

        if event.type == SUMMARIZE_EVENT:
            print("Summarizing data...")
            summarize_data(data_dict, sound_playing)
            sound_playing = "Blank"
            rand_side = "neither"
            pygame.time.set_timer(RESUME_EVENT, time_between_sounds, loops=1)
        
        if event.type == RESUME_EVENT:
            print("Resuming...")
            last_stable_time = time.time()
            running_test = False
            override = False
    
    # Check for user input
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key.isdigit():
            key_num = int(key)
            if key_num == 0:
                print("\nExiting...\n")
                break
            elif key_num == 1:
                print("\nOverriding...\n")
                override = True
    

# Save Data
df = pd.DataFrame(data_dict).T
df.to_csv(f"data/{data_file_name}_{timestamp}.csv", index=False)

# Calculate mean and standard deviation for each sound group
clear_terminal()
sound_stats = df.groupby('sound').agg({'angle': ['mean', 'std'], 'X': ['mean', 'std']})
sound_stats.columns = ['mean_angle', 'std_dev_angle', 'mean_X', 'std_dev_X']
print(sound_stats)

plt.close()
# plot_final(data_dict, sound_set)




