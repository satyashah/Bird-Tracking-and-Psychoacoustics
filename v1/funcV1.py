from globalsV1 import *
 
# Sound
def play_sound():
    pygame.mixer.stop()
    channel = 0 if RUNNINGVARS["speaker_side_playing"] == "left" else 1
    
    if RUNNINGVARS["sound_playing"] != "control":
        pygame.mixer.Channel(channel).play(random.choice(SOUNDSET[RUNNINGVARS["sound_playing"]]), loops=-1)
    
    pygame.mixer.Channel(0).set_volume(1.0, 0.0) # Full volume on left, mute on right
    pygame.mixer.Channel(1).set_volume(0.0, 1.0) # Mute on left, full volume on right

    pygame.time.set_timer(STOP_SOUND_EVENT, PARAMS["sound_duration"], loops=1)

    RUNNINGVARS["sound_A_count"] += 1 if RUNNINGVARS["sound_playing"] == list(SOUNDSET.keys())[0] else 0
    RUNNINGVARS["sound_B_count"] += 1 if RUNNINGVARS["sound_playing"] == list(SOUNDSET.keys())[1] else 0
    RUNNINGVARS["control_count"] += 1 if RUNNINGVARS["sound_playing"] == "control" else 0

    return

# Frame
def get_beak_center(frame):
    """
    This function takes an image and returns the center of the beak.
    """
    # Define BGR range for the color red
    lower_red_bgr = np.array([0, 0, 70])   # Lower bound of red (in BGR format)
    upper_red_bgr = np.array([20, 30, 255])  # Upper bound of red (in BGR format) 

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

    # Plot red indices
    return median_x, median_y, red_indices

def calculate_angle(center, beak_center):
    # Not allowed to switch direction during testing

    if RUNNINGVARS["bird_dir"] == None:
        RUNNINGVARS["bird_dir"] = "north" if beak_center[1] < center[1] else "south"

    dx = beak_center[0] - center[0]
    dy = beak_center[1] - center[1]

    dy = -dy if RUNNINGVARS["bird_dir"] == "north" else dy
    angle = math.degrees(math.atan2(dx, dy))

    if abs(angle) > PARAMS["switch_thresh"]:
        RUNNINGVARS["bird_dir"] = "north" if RUNNINGVARS["bird_dir"] == "south" else "south"
        angle = math.nan

    return angle

# Feed
def display_camara():
    # Read a frame from the video
    frame = FEED.get_cropped_frame()

    # Get the center of the beak
    beak_center_x, beak_center_y, red_indices = get_beak_center(frame)

    # Get the Angle of the beak
    angle = calculate_angle(RUNNINGVARS["cam_center"], (beak_center_x, beak_center_y))

    return frame, angle, (beak_center_x, beak_center_y), red_indices

# Function to plot bird
def plot_bird(cropped_frame, beak_center, angle, red_indices):
    CAM_PLOT.clear()
    CAM_PLOT.imshow(cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB), cmap='gray')
    # CAM_PLOT.scatter(FEED.frame_size//2, FEED.frame_size//2, c='r')
    CAM_PLOT.scatter(RUNNINGVARS["cam_center"][0], RUNNINGVARS["cam_center"][1], c='r')
    CAM_PLOT.scatter(red_indices[1], red_indices[0], s=1)

    if not math.isnan(angle):
        # CAM_PLOT.plot([FEED.frame_size//2, beak_center[0]], [FEED.frame_size//2, beak_center[1]], c='r')
        CAM_PLOT.plot([RUNNINGVARS["cam_center"][0], beak_center[0]], [RUNNINGVARS["cam_center"][1], beak_center[1]], c='r')
        CAM_PLOT.scatter(beak_center[0], beak_center[1], c='r')
        CAM_PLOT.text(280, 50, f'Ang: {angle:.2f}\nX: {beak_center[0] - FEED.frame_size//2:.2f}', color='black', fontsize=12, backgroundcolor='white')
    
    plt.pause(.00000001)

def plot_point(time, angle):
    direction_constant = -1 if RUNNINGVARS["speaker_side_playing"] == "left" else 1

    if RUNNINGVARS["sound_playing"] == list(SOUNDSET.keys())[0]:
        DATA_PLOT = DATA_PLOT_TOP
    elif RUNNINGVARS["sound_playing"] == list(SOUNDSET.keys())[1]:
        DATA_PLOT = DATA_PLOT_BOTTOM
    else:
        DATA_PLOT = DATA_PLOT_CONTROL
    
    pt = DATA_PLOT.plot(time, angle * direction_constant, marker='o', markersize=2, color="red", label='Added Point')

def summarize_points():
    
    if RUNNINGVARS["sound_playing"] == list(SOUNDSET.keys())[0]:
        DATA_PLOT = DATA_PLOT_TOP
    elif RUNNINGVARS["sound_playing"] == list(SOUNDSET.keys())[1]:
        DATA_PLOT = DATA_PLOT_BOTTOM
    else:
        DATA_PLOT = DATA_PLOT_CONTROL
    
    
    filtered_df = DATA[DATA['sound'] == RUNNINGVARS["sound_playing"]]
    if len(filtered_df) > 1:
        average_values = filtered_df.groupby(filtered_df.sound_index)["angle"].mean()
        error_values = filtered_df.groupby(filtered_df.sound_index)["angle"].std(ddof=0)
        DATA_PLOT.plot(average_values.index*PARAMS["sample_rate"], average_values.values, color="purple", label='Average Angle')
        DATA_PLOT.fill_between(list(average_values.index*PARAMS["sample_rate"]), list(average_values.values-error_values.values), list(average_values.values+error_values.values), color="blue", alpha=0.2)

# Data
def data_worker(data_bus, wait_time):
    time.sleep(wait_time/1000)
    record_data()
    data_bus.put([wait_time, RUNNINGVARS["cur_angle"]])
    RUNNINGVARS["sound_frame"] += 1

def spawn_data_collection():
    DATA_BUS.empty()
    threads = []
    for i in range(1 + (PARAMS["data_collection_duration"] // PARAMS["sample_rate"])):
        t = threading.Thread(target=data_worker, args=(DATA_BUS, i * PARAMS["sample_rate"],))
        threads.append(t)
        t.start()

    return threads

def data_socket():
    if len(RUNNINGVARS["threads"]) == 0:
        return
    
    if RUNNINGVARS["thread_index"] == len(RUNNINGVARS["threads"]):
        RUNNINGVARS["threads"] = []
        RUNNINGVARS["thread_index"] = 0

        RUNNINGVARS["sound_frame"] = 0
        pygame.time.set_timer(RESUME_EVENT, PARAMS["time_between_sounds"], loops=1)
        set_data_plots()
        summarize_points()
        return

    
    threads = RUNNINGVARS["threads"]
    if not threads[RUNNINGVARS["thread_index"]].is_alive():
        threads[RUNNINGVARS["thread_index"]].join()
        thread_data = DATA_BUS.get()
        plot_point(thread_data[0], thread_data[1])
        RUNNINGVARS["thread_index"] += 1

def record_data():
    global DATA

    direction_constant = -1 if RUNNINGVARS["speaker_side_playing"] == "left" else 1  # Translate L/R to Toward/Away

    # Create a new row for the current frame
    new_row = {
        'time': round(time.time() - RUNNINGVARS["start_time"], 2),
        'sound_index': RUNNINGVARS["sound_frame"],
        'angle': round(RUNNINGVARS["cur_angle"], 2) * direction_constant,
        'sound': RUNNINGVARS["sound_playing"],
        'side': RUNNINGVARS["speaker_side_playing"]
    }

    # Append the new row to the DataFrame
    if len(DATA) == 0:
        DATA = pd.DataFrame(new_row, index=[0])
    else:
        DATA = pd.concat([DATA, pd.DataFrame(new_row, index=[0])], ignore_index=True)

def reset_data():
    global DATA
    DATA = pd.DataFrame()
    RUNNINGVARS["sound_playing"] = "blank"
    RUNNINGVARS["speaker_side_playing"] = "neither"
    RUNNINGVARS["sound_A_count"] = 0
    RUNNINGVARS["sound_B_count"] = 0
    RUNNINGVARS["control_count"] = 0

    set_data_plots()
# Other Functions
clear_terminal = lambda: os.system('cls')

def bird_stable(angle, beak_center):
    if math.isnan(angle) or abs(angle) > PARAMS["stable_threshold"] or abs(beak_center[1] - RUNNINGVARS["cam_center"][1]) > PARAMS["location_threshold"] or RUNNINGVARS["last_stable_time"] is None:
        RUNNINGVARS["last_stable_time"] = time.time()
    
    if RUNNINGVARS["override"] or (not RUNNINGVARS["running_test"] and time.time() - RUNNINGVARS["last_stable_time"] > PARAMS["stable_duration"]/1000):
        return True

    return False

def get_weight():
    A_count = RUNNINGVARS["sound_A_count"]
    B_count = RUNNINGVARS["sound_B_count"]

    count_dif = 1/(abs(A_count - B_count) + 2)
    A_weight = count_dif if A_count > B_count else 1 - count_dif
    B_weight = 1 - count_dif if A_count > B_count else count_dif

    return [A_weight, B_weight]

def saveData():
    global DATA

    if DATA.empty:
        print("No data to save")
        return
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    plt.savefig(f'data/{timestamp}.png')
    DATA.to_csv(f'data/{timestamp}.csv', index=False)

    clear_terminal()
    
    summarized_data = DATA.groupby('sound').agg({
        'angle': {'mean', 'std', 'min', 'max'},
    })

    # Displaying the summarized data in a neat table format
    print(summarized_data)

















