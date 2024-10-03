from globals import *
from func import *

import time
starttime = time.time()

clear_terminal() # Clear terminal
print("Paused... Press Space here to Resume")

count = 0
while True:
    if RUNNINGVARS["pause"]:
        write2plot(f"Paused... Press Space on Terminal to Resume")
    else:
        write2plot(f"Playing {RUNNINGVARS["sound_playing"]} from {RUNNINGVARS["speaker_side_playing"]} side")

    RUNNINGVARS["frame_num"] += 1
    frame, angle, beak_center, red_indices = display_camara()
    plot_bird(frame, beak_center, angle, red_indices)
    RUNNINGVARS["cur_angle"] = angle
    

    # time.delay(10000)
    # if RUNNINGVARS["pause"]:
    #     if msvcrt.kbhit():
    #         key = msvcrt.getch()
    #         if key == b' ':
    #             print("Resume...\n")
    #             RUNNINGVARS["pause"] = False
    #     continue

    # if bird_stable(angle, beak_center):
    #     print("Bird is stable")
    #     RUNNINGVARS["running_test"] = True
    #     RUNNINGVARS["override"] = False

    #     RUNNINGVARS["sound_playing"] = random.choices(list(SOUNDSET.keys()), weights=get_weight())[0]
    #     RUNNINGVARS["sound_playing"] = "control" if random.random() < PARAMS["control_freq"] else RUNNINGVARS["sound_playing"] # % chance of control sound

    #     RUNNINGVARS["speaker_side_playing"] = random.choice(["left", "right"])
        
    #     print(f"\n{RUNNINGVARS["sound_playing"]} starting on {RUNNINGVARS["speaker_side_playing"]} Speaker...\n")
    #     play_sound()
    #     RUNNINGVARS["threads"] = spawn_data_collection()
    
    # data_socket()

    # for event in pygame.event.get():
    #     if event.type == STOP_SOUND_EVENT:
    #         print("Stopping sound")
    #         pygame.mixer.stop()

    #     if event.type == RESUME_EVENT:
    #         print("Resuming...")
    #         RUNNINGVARS["sound_playing"] = "blank"
    #         RUNNINGVARS["speaker_side_playing"] = "neither"
    #         RUNNINGVARS["last_stable_time"] = time.time()
    #         RUNNINGVARS["running_test"] = False
    #         RUNNINGVARS["override"] = False
    

    """
    Key Presses
        Space: Pause/Resume
        Esc: Exit
        Del: Clear Data
        Enter: Override Testing
    """
    
    if msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b' ':
            print("Paused...")
            RUNNINGVARS["pause"] = True
        if key == b'\x1b':
            print("Exiting...")
            break
        if key == b'\xe0':
            print("Clearing...")
            clear_terminal()
            reset_data()
        if key == b'\r' and not RUNNINGVARS["running_test"]:
            print("Overriding...")
            RUNNINGVARS["override"] = True
        
        key = None


saveData()