PARAMS = {
    ## 
    "control_sound_path": "test_sounds/ABCD_perry.wav",
    
    "sound_names": ["CanaryAB", "tg_ABCDEallrev_bear_40ms"],
    "sound_paths": ["test_sounds/CanaryAB.wav", "test_sounds/tg_ABCDEallrev_bear_40ms.wav"],

    "collection_delay": 3000,  # Delay in ms after sound ends to collect data

    "min_sound_delay": 5000,  # Delay in ms between sounds (must be greater than collection_delay)
    "max_sound_delay" : 20000, # Maximum delay in ms between sounds
    "control_prob": 70,  # Probability of control sound in percentage
    "target_prob": 30,  # Target angle of the bird

    "angle_type": "relative",  # "absolute" or "relative" angle of the bird
 
}

# Fix 109 Globals



