from globalsV8 import *
from testfunc import *

import time
starttime = time.time()

clear_terminal() # Clear terminal

count = 0
while True:

    RUNNINGVARS["frame_num"] += 1
    frame, angle, beak_center, red_indices = display_camara()
    plot_bird(frame, beak_center, angle, red_indices)

    if bird_stable(angle):
        print("Bird is stable")
        RUNNINGVARS["running_test"] = True
        RUNNINGVARS["override"] = False

        RUNNINGVARS["sound_playing"] = random.choices(list(SOUNDSET.keys()), weights=get_weight())[0]
        RUNNINGVARS["speaker_side_playing"] = random.choice(["left", "right"])
        
        print(f"\n{RUNNINGVARS["sound_playing"]} Starting on {RUNNINGVARS["speaker_side_playing"]} Speaker...\n")
        play_sound()
    
    for event in pygame.event.get():
        if event.type == STOP_SOUND_EVENT:
            print("Stopping sound")
            pygame.mixer.stop()

        if event.type == GET_POINT_EVENT:
            
            print(f"{RUNNINGVARS["sound_frame"]}: Getting point at {1000*(time.time() - starttime)}...")
            starttime = time.time()
            record_data(angle, beak_center)
            plot_point(angle)

            if RUNNINGVARS["sound_frame"] == PARAMS["data_collection_duration"] // PARAMS["sample_rate"]:
                print("Summarizing...")
                RUNNINGVARS["sound_frame"] = 0
                pygame.time.set_timer(RESUME_EVENT, PARAMS["time_between_sounds"], loops=1)
                set_data_plots()
                summarize_points()

            RUNNINGVARS["sound_frame"] += 1

        if event.type == RESUME_EVENT:
            print("Resuming...")
            last_stable_time = time.time()
            RUNNINGVARS["running_test"] = False
            RUNNINGVARS["override"] = False
            print(3/0)
            
