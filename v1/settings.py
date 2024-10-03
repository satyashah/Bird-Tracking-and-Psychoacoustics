PARAMS = {

    ## The following are the Sound A and Sound B names to be displayed in the plots and final data sheets
    "sound_A_name": "heteropecific sounds",
    "sound_B_name": "conspecific sounds",


    ## Upload the paths to test_sounds folder and place in its respective sound list. It should be formated as ["test_sounds/ABCD_perry.wav", "test_sounds/ZFAB.wav"]
    "sound_A_paths": ["test_sounds/CanaryAB.wav", "test_sounds/pu995_ABCDEFG.wav"],
    "sound_B_paths": ["test_sounds/ABCD_perry.wav", "test_sounds/tg_ABCDEallrev_bear_40ms.wav"],


    ## These settings determine that the bird is looking forward, stable, and correct location
    "stable_threshold": 25, # Bird must be within +/- this angle to be considered stable
    "location_threshold": 100, # Bird must be within +/- this distance from the center to be considered stable
    "stable_duration": 1000, # Time (ms) the bird must be considered stable before starting test
    

    ## These settings determine the data collection settings
    "data_collection_duration": 3000, # How long the data will be recorded per sample (ms)
    "sound_duration": 1000, # How long the sound will play (ms)
    "sample_rate": 100, # Number of ms before each data sample during collection (i.e. Data collection per X ms)
    "time_between_sounds": 9000, # Minimum time to wait between successive sounds (ms)


    ## Others
    "switch_thresh": 145, # Angle threshold to switch direction of calculate angle
    "resolution": 120, # The plot angle range will be between +/- of the resultion (i.e. for 120 the y-axis will be 120 to -120 degrees)
    "control_freq": 0.25, # Frequency of control sound playing [0.1 == 10%]
}



