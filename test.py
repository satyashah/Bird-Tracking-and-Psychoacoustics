import matplotlib.pyplot as plt
import time


point1 = (0, 0)
point2 = (1, 1)

plt.scatter(point1[0], point1[1], c='r')
plt.pause(2)  # Pause for 2 seconds

plt.clf()  # Clear the previous plot
plt.scatter(point2[0], point2[1], c='r')  # Plot the new point
plt.pause(2)  # Pause for 2 seconds to display the new plot
# plt.show()