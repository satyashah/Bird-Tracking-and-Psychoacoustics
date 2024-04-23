import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time

df_path = "data/test_data_2024-04-18_11-29-22.csv"
df = pd.read_csv(df_path)

new_df = pd.DataFrame(columns=["time", "angle", "X", "Y", "sound"])

for i in range(1, len(df)):
    new_df = new_df._append(df.loc[i-1], ignore_index=True)
    print("Added:", new_df.loc[i-1])

    if i > 100:
        # Group data by 'sound' column
        grouped = df.groupby('sound')
        sound_stats = df.groupby('sound').agg({'angle': ['mean', 'std'], 'X': ['mean', 'std']})

        sound_stats.columns = ['mean_angle', 'std_dev_angle', 'mean_X', 'std_dev_X']

        # Extract data for plotting
        sounds = sound_stats.index
        mean_angles = sound_stats['mean_angle']
        std_angles = sound_stats['std_dev_angle']

        # Plotting
        plt.errorbar(np.arange(len(sounds)), mean_angles, yerr=std_angles, fmt='o')
        plt.xticks(np.arange(len(sounds)), sounds)
        plt.xlabel('Sound')
        plt.ylabel('Mean Angle')
        plt.title('Mean Angle with Standard Deviation as Error Bars')
        plt.xticks(rotation=-30)
        plt.grid(True)
        plt.show()