from funcV6 import *

# User Params [CHANGE THESE]
FRAME_SIZE = 400

# left_sound_paths = ["test_sounds/ABCD_perry.wav", "test_sounds/CanaryAB.wav", "test_sounds/pu995_ABCDEFG.wav"]
# right_sound_paths = ["test_sounds/ABCD_perry.wav", "test_sounds/CanaryAB.wav", "test_sounds/pu995_ABCDEFG.wav"]

sound_A_path = "test_sounds/ABCD_perry.wav"
sound_B_path = "test_sounds/CanaryAB.wav"

sound_duration = 1000
data_collection_duration = 3000 # note this starts at beginning of sound
time_between_sounds = 5000


stable_threshold = (-15, 15, 5) # (min, max, time to be stable for)
last_stable_time = time.time()

# System Params [DO NOT CHANGE]
clear_terminal()

# x,y = set_up_cam()
center_cords = (337, 211) #(x, y)

data_file_name = "test_data"

STOP_SOUND_EVENT = pygame.USEREVENT + 1
SUMMARIZE_EVENT = pygame.USEREVENT + 2
RESUME_EVENT = pygame.USEREVENT + 3

frame_num = 0
data_dict = {}
start_time = time.time()
sound_playing = "Blank"

# Setup Sound
sound_set = set_up_sound(sound_A_path, sound_B_path)
print("Sound Loaded:",sound_set.keys())


# Application
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
print(f"Application started... {timestamp}")

# Live Feed
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
ret, frame = cap.read(0) # Remove first frame

running_test = False


# Create a figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

plotA = ax1 
plotB = ax2
plt.tight_layout(pad=2)

while True:
    frame_num += 1
    
    # Check the Video Feed
    try:
        cropped_frame, angle, beak_center = display_camara(cap, center_cords, FRAME_SIZE)
        plot_bird(cropped_frame, beak_center, angle, FRAME_SIZE, plotA)
    except Exception as e:
        print(f"Error: {e}")
        break
        continue
    
    # Reset the timer if the bird is not stable
    if angle < stable_threshold[0] or angle > stable_threshold[1] or beak_center[1] - FRAME_SIZE//2 < 0:
        last_stable_time = time.time()

    # Start the test if the bird is stable and a test is not already running
    if not running_test and time.time() - last_stable_time > stable_threshold[2]:
        print("Bird is stable") 
        running_test = True

        rand_sound = random.choice(list(sound_set.keys()))
        rand_side = random.choice(["left", "right"])

        # Run code to play sound
        if sound_playing == rand_sound:
            data_dict[frame_num] = {
                'time': round(time.time() - start_time,2), 
                'angle': round(angle,2), 
                'X': beak_center[0] - FRAME_SIZE//2, 
                'Y': beak_center[1] - FRAME_SIZE//2, 
                'sound': "None"
            }

            frame_num += 1

        print(f"\n{rand_sound} Starting on {rand_side} Speaker...\n")
        print(f"Initial \n\tAngle => {round(angle,2)} \n\tX => {beak_center[0] - FRAME_SIZE//2}\n")
        play_sound(sound_set[rand_sound], rand_side, sound_duration, STOP_SOUND_EVENT, data_collection_duration, SUMMARIZE_EVENT)
        sound_playing = rand_sound
    

    # Save Data
    data_dict[frame_num] = {}
    data_dict[frame_num]["time"] = round(time.time() - start_time,2)
    data_dict[frame_num]["angle"] = round(angle,2)
    data_dict[frame_num]["X"] = beak_center[0] - FRAME_SIZE//2
    data_dict[frame_num]["Y"] = beak_center[1] - FRAME_SIZE//2
    data_dict[frame_num]["sound"] = sound_playing

    plot_mean(data_dict, data_dict[frame_num], plotB)
    
    # Events to maintain the application
    for event in pygame.event.get():
        if event.type == STOP_SOUND_EVENT:
            print("Stopping sound")
            pygame.mixer.stop()

        if event.type == SUMMARIZE_EVENT:
            print("Summarizing data...")
            summarize_data(data_dict, sound_playing)
            sound_playing = "Blank"
            pygame.time.set_timer(RESUME_EVENT, time_between_sounds, loops=1)
        
        if event.type == RESUME_EVENT:
            print("Resuming...")
            last_stable_time = time.time()
            running_test = False
    
    # Check for user input
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key.isdigit():
            break
    


# Save Data
df = pd.DataFrame(data_dict).T
df.to_csv(f"data/{data_file_name}_{timestamp}.csv", index=False)

# Calculate mean and standard deviation for each sound group
sound_stats = df.groupby('sound').agg({'angle': ['mean', 'std'], 'X': ['mean', 'std']})
sound_stats.columns = ['mean_angle', 'std_dev_angle', 'mean_X', 'std_dev_X']
print(sound_stats)

get_time_plots(df)
plot_summarized_data(sound_stats)

