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
        write2plot(f"Playing {RUNNINGVARS['sound_playing'][0]} from {RUNNINGVARS['speaker_side_playing']} side")

    frame, angle, beak_center, red_indices = display_camara()
    plot_bird(frame, beak_center, angle, red_indices)
    RUNNINGVARS["cur_angle"] = random.randint(-50, 50) # angle

    if RUNNINGVARS["pause"]:
        if msvcrt.kbhit():
            if msvcrt.getch() == b' ':
                print("Resume...\n")
                RUNNINGVARS["pause"] = False
        continue

    if not RUNNINGVARS["running_test"] and not RUNNINGVARS["pause_between_stims"]:
        RUNNINGVARS["stim_num"] += 1

        if RUNNINGVARS["stim_num"] == 0:
            RUNNINGVARS["speaker_side_playing"] = random.choice(["left", "right"])

        if RUNNINGVARS["stim_num"] == len(TRIALS[RUNNINGVARS["trial_num"]]):
            RUNNINGVARS["stim_num"] = 0
            RUNNINGVARS["trial_num"] += 1
            summarize_trial()

        if RUNNINGVARS["trial_num"] == len(TRIALS):
            write2plot("Complete")
            break
        
        RUNNINGVARS["sound_playing"] = TRIALS[RUNNINGVARS["trial_num"]][RUNNINGVARS["stim_num"]]
        print("Playing", RUNNINGVARS["sound_playing"][0], "from", RUNNINGVARS["speaker_side_playing"], "side")
        RUNNINGVARS["running_test"] = True
        play_sound()
    
    if not RUNNINGVARS["pause_between_stims"]:
        record_data()

    for event in pygame.event.get():
        if event.type == STOP_SOUND_EVENT:
            print("Completed Stimulus:", f"{RUNNINGVARS['trial_num']}.{RUNNINGVARS['stim_num']}")
            RUNNINGVARS["running_test"] = False
            plot_point()
            pygame.mixer.stop()
            RUNNINGVARS["pause_between_stims"] = True
            pygame.time.set_timer(RESUME_EVENT, PARAMS["time_between_stimulus"] * 1000, loops=1)
        if event.type == RESUME_EVENT:
            RUNNINGVARS["pause_between_stims"] = False


    # Key Presses
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b' ':
            print("Paused...")
            RUNNINGVARS["pause"] = True
        elif key == b'\x1b':
            print("Exiting...")
            break
        elif key == b'\xe0':
            print("Clearing...")
            clear_terminal()
        elif key == b'\r' and not RUNNINGVARS["running_test"]:
            print("Overriding...")
            RUNNINGVARS["override"] = True

saveData()
plt.pause(1000)
