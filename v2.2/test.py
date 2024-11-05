import pandas as pd 
import numpy as np

DATA = pd.read_csv('data/raw_2024-11-04_12-33-19.csv')

import matplotlib.pyplot as plt
from numpy import polyfit


def average_polynomial_curve(DATA):
    """
    This function calculates the average polynomial curve for each unique sound
    by fitting a polynomial to the time vs. angle data of each stim_code (trial) and then averaging the fitted curves.
    
    Arguments:
    - DATA: pandas DataFrame with the columns ['stim_code', 'time', 'angle', 'sound', 'side']
    - poly_degree: The degree of the polynomial to fit to each stim_code's time-angle data (default is 3).
    
    Returns:
    - avg_curves: A dictionary where the keys are sound types, and the values are the averaged polynomial curves.
    """

    # 1. Group the data by 'sound' to get separate groups of trials
    grouped = DATA.groupby('sound')
    poly_degree = 10

    # Dictionary to store the average polynomials for each sound
    avg_curves = {}

    for sound, group in grouped:
        polynomials = []
        max_time = 0
        # 2. For each sound, loop through each stim_code (trial) and fit a polynomial to it
        for stim_code, stim_data in group.groupby('stim_code'):
            stim_data['time'] = stim_data['time'] - stim_data['time'].min()
            stim_data['angle'] = stim_data['angle'] - stim_data['angle'].iloc[0]
            # Fit a polynomial to the time vs. angle data for this stim_code
            p = polyfit(stim_data['time'], stim_data['angle'], poly_degree)
            # Skip NaN values
            if np.isnan(p).any():
                continue

            polynomials.append(p)
            max_time = max(max_time, stim_data['time'].max())

        
        # Create an array for each second
        time_points = np.linspace(0, max_time, num=int(max_time*100))
        avg_curve = [0] * len(time_points)

        # Initialize a list to store the polynomial values at each time point for each polynomial
        poly_values = np.zeros((len(polynomials), len(time_points)))

        for idx, p in enumerate(polynomials):
            poly_values[idx] = np.polyval(p, time_points)

        # Calculate the mean and standard deviation at each time point
        avg_curve = np.mean(poly_values, axis=0)
        std_dev = np.std(poly_values, axis=0)

        # Plot the average polynomial curve with error bars
        plt.plot(time_points, avg_curve, label=sound)
        plt.fill_between(time_points, avg_curve - std_dev, avg_curve + std_dev, alpha=0.2)

    plt.xlabel('Time')
    plt.ylabel('Angle')
    plt.title('Average Polynomial Curves for Each Sound')
    plt.legend()
    plt.show()

            

average_polynomial_curve(DATA)