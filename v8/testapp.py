from globalsV8 import *
from testfunc import *

clear_terminal() # Clear terminal


while True:
    frame, angle, beak_center, red_indices = display_camara()
    plot_bird(frame, beak_center, angle, red_indices)

    if bird_stable(angle):
        print("Bird is stable")
        RUNNINGVARS["running_test"] = True
        RUNNINGVARS["override"] = False

        rand_sound = random.choices(list(SOUNDSET.keys()), weights=get_weight())[0]
        rand_side = random.choice(["left", "right"])
        

    
    