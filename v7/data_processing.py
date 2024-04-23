import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
from scipy.stats import norm

df_path = "data/test_data_2024-04-18_11-29-22.csv"
df = pd.read_csv(df_path)

new_df = pd.DataFrame(columns=["time", "angle", "X", "Y", "sound"])

for i in range(1, len(df)):
    new_df = new_df._append(df.loc[i-1], ignore_index=True)
    

    if i > 100:
        # Group data by 'sound' column
        grouped = new_df.groupby('sound')
        sound_stats = grouped.agg({'angle': ['mean', 'std', 'size'], 'X': ['mean', 'std']})

        sound_stats.columns = ['mean_angle', 'std_dev_angle', 'sample_size', 'mean_X', 'std_dev_X']

        # Extract data for plotting
        sounds = sound_stats.index
        mean_angles = sound_stats['mean_angle']
        std_angles = sound_stats['std_dev_angle']

        print("Added:", new_df.loc[i-1]["sound"], mean_angles[new_df.loc[i-1]["sound"]], std_angles[new_df.loc[i-1]["sound"]])

        # Build 95% confidence interval
        n = len(sound_stats['sample_size'])
        z = norm.ppf(0.975)  # 0.975 for two-tailed test
        margin_of_error = z * (sound_stats['std_dev_angle'] / np.sqrt(n))


        # Plotting
        plt.clf()
        plt.errorbar(np.arange(len(sounds)), mean_angles, yerr=margin_of_error, fmt='o', c = 'b')
        plt.xticks(np.arange(len(sounds)), sounds, c = 'b')
        plt.xlabel('Sound')
        plt.ylabel('Mean Angle')
        plt.title('Mean Angle with Standard Deviation as Error Bars')
        plt.xticks(rotation=-30)

        plt.plot(
            sounds.get_loc(new_df.loc[i-1]["sound"]), 
            new_df.loc[i-1]["angle"], 
            marker='o', markersize=10, color='red', label='Added Point')


        plt.grid(True)
        plt.pause(.00000001)