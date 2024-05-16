from globalsV8 import *
from funcV8 import *

import time
starttime = time.time()

clear_terminal() # Clear terminal

count = 0
while True:
    TOP_PLOT.clear()
    TOP_PLOT.axis("off")
    TOP_PLOT.text(0.5, 0.5, f"Playing {RUNNINGVARS["sound_playing"]} from {RUNNINGVARS["speaker_side_playing"]} side", fontsize=20, ha="center", va="center")
            
    RUNNINGVARS["frame_num"] += 1
    frame, angle, beak_center, red_indices = display_camara()
    plot_bird(frame, beak_center, angle, red_indices)
    RUNNINGVARS["cur_angle"] = angle

    if bird_stable(angle):
        print("Bird is stable")
        RUNNINGVARS["running_test"] = True
        RUNNINGVARS["override"] = False

        RUNNINGVARS["sound_playing"] = random.choices(list(SOUNDSET.keys()), weights=get_weight())[0]
        RUNNINGVARS["speaker_side_playing"] = random.choice(["left", "right"])
        
        print(f"\n{RUNNINGVARS["sound_playing"]} Starting on {RUNNINGVARS["speaker_side_playing"]} Speaker...\n")
        play_sound()
        RUNNINGVARS["threads"] = spawn_data_collection()
    
    data_socket()

    
    for event in pygame.event.get():
        if event.type == STOP_SOUND_EVENT:
            print("Stopping sound")
            
            pygame.mixer.stop()

        if event.type == RESUME_EVENT:
            print("Resuming...")
            RUNNINGVARS["sound_playing"] = "blank"
            RUNNINGVARS["speaker_side_playing"] = "neither"
            last_stable_time = time.time()
            RUNNINGVARS["running_test"] = False
            RUNNINGVARS["override"] = False
            
