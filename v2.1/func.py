from globals import *

# Sound
def play_sound():
    pygame.mixer.stop()
    channel = 0 if RUNNINGVARS["speaker_side_playing"] == "left" else 1

    pygame.mixer.Channel(channel).play(RUNNINGVARS["sound_playing"][1], loops=-1)
    pygame.mixer.Channel(0).set_volume(1.0, 0.0)  # Full volume on left
    pygame.mixer.Channel(1).set_volume(0.0, 1.0)  # Full volume on right

    pygame.time.set_timer(STOP_SOUND_EVENT, int(RUNNINGVARS["sound_playing"][1].get_length() * 1000), loops=1)

# Frame
def get_beak_center(frame):
    """ Returns the center of the beak from the frame. """
    lower_red_bgr = np.array([0, 0, 70])
    upper_red_bgr = np.array([50, 30, 255])

    mask = cv2.inRange(frame, lower_red_bgr, upper_red_bgr)
    red_indices = np.where(mask != 0)

    if red_indices[0].size != 0:
        median_x = np.median(red_indices[1])
        median_y = np.median(red_indices[0])
    else:
        median_x, median_y = np.nan, np.nan

    return median_x, median_y, red_indices

def calculate_angle(center, beak_center):
    dx = beak_center[0] - center[0]
    dy = beak_center[1] - center[1]
    angle = math.degrees(math.atan2(dx, dy))
    return angle

# Feed
def display_camara():
    frame = FEED.get_cropped_frame()
    beak_center_x, beak_center_y, red_indices = get_beak_center(frame)
    angle = calculate_angle(RUNNINGVARS["cam_center"], (beak_center_x, beak_center_y))
    return frame, angle, (beak_center_x, beak_center_y), red_indices

# Function to plot bird
def plot_bird(cropped_frame, beak_center, angle, red_indices):
    CAM_PLOT.clear()
    CAM_PLOT.imshow(cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB), cmap='gray')
    CAM_PLOT.scatter(RUNNINGVARS["cam_center"][0], RUNNINGVARS["cam_center"][1], c='r')
    CAM_PLOT.scatter(red_indices[1], red_indices[0], s=1)

    if not math.isnan(angle):
        CAM_PLOT.plot([RUNNINGVARS["cam_center"][0], beak_center[0]], 
                      [RUNNINGVARS["cam_center"][1], beak_center[1]], c='r')
        CAM_PLOT.scatter(beak_center[0], beak_center[1], c='r')
        CAM_PLOT.text(280, 50, f'Ang: {angle:.2f}\nX: {beak_center[0] - FEED.frame_size//2:.2f}', 
                      color='black', fontsize=12, backgroundcolor='white')
    
    plt.pause(0.00000001)

def plot_point():
    if RUNNINGVARS["sound_playing"][0] == "control_pass":
        return

    stim_code = f"{RUNNINGVARS['trial_num']}.{RUNNINGVARS['stim_num']}"
    stim_data = DATA[DATA['stim_code'] == stim_code]
    
    # Use Either
    last_angle_change = stim_data['angle'].iloc[-1] - stim_data['angle'].iloc[0]
    middle_angle = stim_data['angle'].iloc[len(stim_data) // 2]

    plot_data = last_angle_change if PARAMS["data_display"] == "angle_change" else middle_angle

    categories = ['control'] + PARAMS["sound_names"]
    DATA_PLOT.scatter(categories.index(RUNNINGVARS["sound_playing"][0]) + 1, plot_data, color="purple")

def summarize_trial():
    data_by_code = DATA.groupby('stim_code').agg(
        duration=('time', lambda x: x.iloc[-1] - x.iloc[0]),
        sound=('sound', 'first'),
        angle_change=('angle', lambda x: x.iloc[-1] - x.iloc[0]),
        middle_angle=('angle', lambda x: x.iloc[len(x) // 2])
    ).reset_index()

    set_data_plots()
    categories = ['control'] + PARAMS["sound_names"]
    angle_changes = [data_by_code[data_by_code['sound'] == category][PARAMS["data_display"]] for category in categories]

    DATA_PLOT.boxplot(angle_changes, labels=categories, showmeans=True)
    print(data_by_code)

# Data
def get_angle_change(stim_code):
    stim_data = DATA[DATA['stim_code'] == stim_code]
    if not stim_data.empty:
        return stim_data['angle'].iloc[-1] - stim_data['angle'].iloc[0]
    return None

def record_data():
    direction_constant = -1 if RUNNINGVARS["speaker_side_playing"] == "left" else 1
    new_row = {
        'stim_code': f"{RUNNINGVARS['trial_num']}.{RUNNINGVARS['stim_num']}",
        'time': round(time.time() - RUNNINGVARS["start_time"], 2),
        'angle': round(RUNNINGVARS["cur_angle"], 2) * direction_constant,
        'sound': RUNNINGVARS["sound_playing"][0],
        'side': RUNNINGVARS["speaker_side_playing"]
    }
    global DATA
    DATA = pd.concat([DATA, pd.DataFrame(new_row, index=[0])], ignore_index=True) if not DATA.empty else pd.DataFrame(new_row, index=[0])

# Other Functions
clear_terminal = lambda: os.system('cls')

def bird_stable(angle, beak_center):
    if (math.isnan(angle) or abs(angle) > PARAMS["stable_threshold"] or
            abs(beak_center[1] - RUNNINGVARS["cam_center"][1]) > PARAMS["location_threshold"] or 
            RUNNINGVARS["last_stable_time"] is None):
        RUNNINGVARS["last_stable_time"] = time.time()
    
    return RUNNINGVARS["override"] or (not RUNNINGVARS["running_test"] and 
           time.time() - RUNNINGVARS["last_stable_time"] > PARAMS["stable_duration"] / 1000)

def saveData():
    global DATA
    if DATA.empty:
        print("No data to save")
        return
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    plt.savefig(f'data/{timestamp}.png')
    DATA.to_csv(f'data/raw_{timestamp}.csv', index=False)

    print(DATA)

    clear_terminal()

    data_by_code = DATA.groupby('stim_code').agg(
        duration=('time', lambda x: x.iloc[-1] - x.iloc[0]),
        sound=('sound', 'first'),
        start_angle=('angle', 'first'),
        angle_change=('angle', lambda x: x.iloc[-1] - x.iloc[0]),
        middle_angle=('angle', lambda x: x.iloc[len(x) // 2])
    ).reset_index()

    summarized_data = data_by_code.groupby('sound').agg(
        mean=('angle_change', 'mean'),
        std=('angle_change', 'std'),
        abs_min=('angle_change', lambda x: x.abs().min()),
        abs_max=('angle_change', lambda x: x.abs().max()),
        count=('angle_change', 'count')
    ).reset_index()

    print("\nAngle By Stimulus Code\n", data_by_code)
    print("\nSummarized Angle Change by Stimulus\n", summarized_data)

    data_by_code.to_csv(f'data/sum_{timestamp}.csv', index=False)
