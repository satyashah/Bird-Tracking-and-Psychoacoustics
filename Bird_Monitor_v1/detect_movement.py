import cv2
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt

# Read the images
bird_pos_image = cv2.imread('test_images/bird_tube_pos_clean.jpg', cv2.IMREAD_GRAYSCALE)
bird_left_image = cv2.imread('test_images/bird_tube_left_clean.jpg', cv2.IMREAD_GRAYSCALE)


# For bird_pos we want to assume the bird is standing straight up and down
coords = np.argwhere(bird_pos_image == 1)
print(coords)

x_avg = np.mean(coords[:, 0])
print(x_avg)
plt.vlines(x_avg, ymin=0, ymax=250, color='r')

plt.imshow(bird_pos_image, cmap='gray')
plt.show()


# Take bird position and convert into a graph where black = 0 and white = 1 based on x and y coordinates
bird_img = bird_left_image

# Find coordinates where bird_graph equals 1
coords = np.argwhere(bird_img > 50)

# Perform linear regression
slope, intercept, _, _, _ = linregress(coords[:, 1], coords[:, 0])

# Generate line of best fit using the slope and intercept
x_values = np.arange(0, 280)
y_values = slope * x_values + intercept

# Plot the line of best fit on bird_graph
plt.plot(x_values, y_values, color='r')

plt.imshow(bird_img, cmap='gray')
plt.show()


# Find the angle of the line of best fit from the horizontal
angle = np.arctan(slope) * 180 / np.pi
print(angle)

# Plot both the lines of best fit and the original bird_graph
plt.vlines(x_avg, ymin=0, ymax=250, color='r')
plt.plot(x_values, y_values, color='r')
plt.imshow(bird_img, cmap='gray')
plt.show()