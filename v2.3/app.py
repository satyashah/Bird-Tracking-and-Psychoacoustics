from globals import *
from func import *
import time
import random  # Added this since random is used

starttime = time.time()

clear_terminal()  # Clear terminal
print("Paused... Press Space here to Resume")



while True:
    if RUNNINGVARS["pause"]:
        write2plot("Paused... Press Space on Terminal to Resume")
    else:
        write2plot(f"{RUNNINGVARS['sound_playing'][0].upper()} : {RUNNINGVARS['speaker_side_playing'].upper()}")

    frame, angle, beak_center, red_indices = display_camara()
    plot_bird(frame, beak_center, angle, red_indices)
    RUNNINGVARS["cur_angle"] = RUNNINGVARS["cur_angle"] + random.randint(-5, 5) #// angle

    if RUNNINGVARS["pause"]:
        
        if msvcrt.kbhit():
            if msvcrt.getch() == b'u':
                user_inputs = get_user_inputs()
                PARAMS.update(user_inputs)
                build_sound_prob_arr()
                print("Updated Parameters")
            if msvcrt.getch() == b' ':
                print("Resume...\n")
                RUNNINGVARS["pause"] = False
                pygame.event.clear()
                pygame.time.set_timer(PLAY_SOUND_EVENT, 5000, loops=0)
        continue

    # Key Presses
    if  msvcrt.kbhit():
        key = msvcrt.getch()

        
        
        # Direction Keys
        if key == b'l':
            print("Speaker Changed to Left")
            RUNNINGVARS["speaker_side_playing"] = "left"
        elif key == b'r':
            print("Speaker Changed to Right")
            RUNNINGVARS["speaker_side_playing"] = "right"

        # Functional Keys
        elif key == b'x':
            print("Marking Data For Exclusion...")
            mark_data()
        elif key == b' ':
            print("Paused...")
            RUNNINGVARS["pause"] = True
        elif key == b'\x1b':
            print("Exiting...")
            
            break
        elif key == b'\xe0':
            print("Clearing...")
            clear_terminal()

    if RUNNINGVARS["sound_playing"][0] != "blank":
        record_data()
        plot_point()
        
    
    for event in pygame.event.get():
        if event.type == PLAY_SOUND_EVENT:
            
            digit = random.sample(SOUND_PROB_ARR,1)[0] # FIX

            if int(digit) == 0:
                print(f"{digit}:control Pressed")
                RUNNINGVARS["sound_playing"] = ("control", pygame.mixer.Sound(PARAMS["control_sound_path"]))
            else:
                sound_name = list(SOUNDSET.keys())[int(digit) - 1]
                print(f"{digit}:{sound_name} Pressed")

                RUNNINGVARS["sound_playing"] = (sound_name, SOUNDSET[sound_name])
            
            set_data_plot()
            RUNNINGVARS["trial_num"] += 1
            play_sound()
            pygame.time.set_timer(PLAY_SOUND_EVENT, random.randint(PARAMS["min_sound_delay"] + PARAMS["collection_delay"], PARAMS["max_sound_delay"] + PARAMS["collection_delay"]), loops=0)

        if event.type == STOP_SOUND_EVENT:
            set_sum_plot()
            summarize_trial()
            average_polynomial_curve()

            print("Completed Trail:", f"{RUNNINGVARS['trial_num']}:{RUNNINGVARS['sound_playing'][0]}\n")
            RUNNINGVARS['sound_playing'] = ("blank", None)
            pygame.mixer.stop()

            
            


saveData()
plt.pause(1000)
