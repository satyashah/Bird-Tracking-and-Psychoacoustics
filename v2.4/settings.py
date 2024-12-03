PARAMS = {
    ## 
    "control_sound_path": "test_sounds/ABCD_perry.wav",
    
    "sound_names": ["CanaryAB", "tg_ABCDEallrev_bear_40ms"],
    "sound_paths": ["test_sounds/CanaryAB.wav", "test_sounds/tg_ABCDEallrev_bear_40ms.wav"],

    "collection_delay": 3000,  # Delay in ms after sound ends to collect data

    "min_sound_delay": 5000, # Minimum Delay in ms between sounds (must be greater than collection_delay)
    "max_sound_delay" : 5000, # Maximum Delay in ms between sounds (must be greater than collection_delay)

    # If you want only manual targets set the following to 0
    "auto_sounds": True, # If true, sounds are played automatically
    "target_prob": 10,  # Probabilty % the target sound is played

    "angle_type": "relative",  # "absolute" or "relative" angle of the bird

    "stab_thresh": 5, # minimum deviation of bird movement to be considered stable
}

# Fix 109 Globals



