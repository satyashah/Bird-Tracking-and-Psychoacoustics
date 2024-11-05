from globals import *

# Sound
def play_sound():
    pygame.mixer.stop()
    channel = 0 if RUNNINGVARS["speaker_side_playing"] == "left" else 1

    pygame.mixer.Channel(channel).play(RUNNINGVARS["sound_playing"][1], loops=0)
    pygame.mixer.Channel(0).set_volume(1.0, 0.0)  # Full volume on left
    pygame.mixer.Channel(1).set_volume(0.0, 1.0)  # Full volume on right

    pygame.time.set_timer(STOP_SOUND_EVENT, int(RUNNINGVARS["sound_playing"][1].get_length() * 1000) + PARAMS["collection_delay"], loops=1)

# Frame
def get_beak_center(frame):
    """ Returns the center of the beak from the frame. """
    lower_red_bgr = np.array([0, 0, 70])
    upper_red_bgr = np.array([50, 30, 255])

    mask = cv2.inRange(frame, lower_red_bgr, upper_red_bgr)
    red_indices = np.where(mask != 0)
    print(red_indices[0].size)
    if red_indices[0].size > 50: # Addition of Min Surface area: != 0:
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

    stim_data = DATA[DATA['stim_code'] == RUNNINGVARS['trial_num']]
    
    # Use Either
    time_elapsed = stim_data['time'].iloc[-1] - stim_data['time'].iloc[0]
    angle_change = stim_data['angle'].iloc[-1] - (stim_data['angle'].iloc[0] if PARAMS["angle_type"] == "relative" else 0)

    DATA_PLOT.scatter(time_elapsed, angle_change, color="purple")

def summarize_trial():
    data_by_code = DATA.groupby('stim_code').agg(
        duration=('time', lambda x: x.iloc[-1] - x.iloc[0]),
        sound=('sound', 'first'),
        start_angle=('angle', 'first'),
        angle_change=('angle', lambda x: x.iloc[-1] - x.iloc[0]),
        max_angle_change = ('angle', lambda x: max(abs(x - x.iloc[0]))),
        middle_angle=('angle', lambda x: x.iloc[len(x) // 2])
    ).reset_index()

    trial_summary = data_by_code[data_by_code['stim_code'] == RUNNINGVARS['trial_num']].iloc[-1].to_dict()
    print("\nTrial Summary:")
    for key, value in trial_summary.items():
        print(f"\t{key}: {value}")

    stim_data = DATA[DATA['stim_code'] == RUNNINGVARS['trial_num']]
    stim_data.loc[:, 'time'] = stim_data['time'] - stim_data['time'].iloc[0]
    stim_data.loc[:, 'angle'] = stim_data['angle'] - (stim_data['angle'].iloc[0] if PARAMS["angle_type"] == "relative" else 0)
    DATA_PLOT.plot(stim_data['time'], stim_data['angle'])
    DATA_PLOT.vlines(RUNNINGVARS["sound_playing"][1].get_length(), ymin=-45, ymax=45, color='r')

def average_polynomial_curve():
    print(DATA)
    included_data = DATA[DATA['included']]
    # 1. Group the data by 'sound' to get separate groups of trials
    grouped = included_data.groupby('sound')
    poly_degree = 10

    # Dictionary to store the average polynomials for each sound
    avg_curves = {}

    for sound, group in grouped:
        polynomials = []
        max_time = 0
        # 2. For each sound, loop through each stim_code (trial) and fit a polynomial to it
        for stim_code, stim_data in group.groupby('stim_code'):
            stim_data['time'] = stim_data['time'] - stim_data['time'].min()
            stim_data['angle'] = stim_data['angle'] - stim_data['angle'].iloc[0]
            # Fit a polynomial to the time vs. angle data for this stim_code
            p = polyfit(stim_data['time'], stim_data['angle'], poly_degree)
            # Skip NaN values
            if np.isnan(p).any():
                continue

            polynomials.append(p)
            max_time = max(max_time, stim_data['time'].max())

        
        # Create an array for each second
        time_points = np.linspace(0, max_time, num=int(max_time*100))
        avg_curve = [0] * len(time_points)

        # Initialize a list to store the polynomial values at each time point for each polynomial
        poly_values = np.zeros((len(polynomials), len(time_points)))

        for idx, p in enumerate(polynomials):
            poly_values[idx] = np.polyval(p, time_points)

        # Calculate the mean and standard deviation at each time point
        avg_curve = np.mean(poly_values, axis=0)
        std_dev = np.std(poly_values, axis=0)

        # Plot the average polynomial curve with error bars
        DATA_PLOT.plot(time_points, avg_curve, label=sound)
        DATA_PLOT.fill_between(time_points, avg_curve - std_dev, avg_curve + std_dev, alpha=0.2)
    
    DATA_PLOT.legend()
    DATA_PLOT.set_title('Average Polynomial Curves for Each Sound')


# Data
def get_angle_change(stim_code):
    stim_data = DATA[DATA['stim_code'] == stim_code]
    if not stim_data.empty:
        return stim_data['angle'].iloc[-1] - stim_data['angle'].iloc[0]
    return None

def record_data():
    direction_constant = -1 if RUNNINGVARS["speaker_side_playing"] == "left" else 1
    new_row = {
        'stim_code': RUNNINGVARS['trial_num'],
        'time': round(time.time() - RUNNINGVARS["start_time"], 2),
        'angle': round(RUNNINGVARS["cur_angle"], 2) * direction_constant,
        'sound': RUNNINGVARS["sound_playing"][0],
        'side': RUNNINGVARS["speaker_side_playing"],
        'included': True
    }
    global DATA
    DATA = pd.concat([DATA, pd.DataFrame(new_row, index=[0])], ignore_index=True) if not DATA.empty else pd.DataFrame(new_row, index=[0])


def mark_data():
    stim_code = RUNNINGVARS['trial_num']
    DATA.loc[DATA['stim_code'] == stim_code, 'included'] = False

# Other Functions
clear_terminal = lambda: os.system('cls')

def saveData():
    global DATA
    if DATA.empty:
        print("No data to save")
        return
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    plt.savefig(f'data/{timestamp}.png')
    DATA.to_csv(f'data/raw_{timestamp}.csv', index=False)

    # Drop rows where 'included' is False
    DATA = DATA[DATA['included']]

    clear_terminal()


    data_by_code = DATA.groupby('stim_code').agg(
        duration=('time', lambda x: x.iloc[-1] - x.iloc[0]),
        sound=('sound', 'first'),
        start_angle=('angle', 'first'),
        angle_change=('angle', lambda x: x.iloc[-1] - x.iloc[0]),
        max_angle_change = ('angle', lambda x: max(abs(x - x.iloc[0]))),
        middle_angle=('angle', lambda x: x.iloc[len(x) // 2])
    ).reset_index()

    summarized_data = data_by_code.groupby('sound').agg(
        mean=('angle_change', 'mean'),
        max_mean=('max_angle_change', 'mean'),
        std=('angle_change', 'std'),
        count=('angle_change', 'count')
    ).reset_index()

    print("\nAngle By Stimulus Code\n", data_by_code)
    print("\nSummarized Angle Change by Stimulus\n", summarized_data)

    data_by_code.to_csv(f'data/sum_{timestamp}.csv', index=False)
