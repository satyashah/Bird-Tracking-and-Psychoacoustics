from globals import *
from func import *


def record_data():
    global DATA

    direction_constant = -1 if RUNNINGVARS["speaker_side_playing"] == "left" else 1  # Translate L/R to Toward/Away

    # Create a new row for the current frame
    new_row = {
        'time': 3,
        'angle': 3,
        'sound': 3,
        'side': 4
    }

    # Append the new row to the DataFrame
    if len(DATA) == 0:
        DATA = pd.DataFrame(new_row, index=[0])
    else:
        DATA = pd.concat([DATA, pd.DataFrame(new_row, index=[0])], ignore_index=True)

record_data()
record_data()
record_data()
record_data()

print(DATA)