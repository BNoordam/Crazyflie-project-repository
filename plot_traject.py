import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = pd.read_csv('traject13_log_Robust_Mellinger_cf2.csv', header=0, delimiter=',', skiprows=0, usecols=[1, 2, 3])
datalist = data.values.tolist()
# Convert figure8 to a NumPy array
data_array = np.array(datalist)

# Your data
x = data_array[:, 0]
y = data_array[:, 1]
z = data_array[:, 2]

ax = plt.figure().add_subplot(projection='3d')

ax.plot(x, y, z, label='3D measured trajectory')

data2 = pd.read_csv('timed_waypoints_yaw13.csv', header=0, delimiter=',', skiprows=0, usecols=[1, 2, 3])
datalist2 = data2.values.tolist()
# Convert figure8 to a NumPy array
data_array2 = np.array(datalist2)

# Your data
x2 = data_array2[:, 0]
y2 = data_array2[:, 1]
z2 = data_array2[:, 2]
ax.plot(x2, y2, z2, label='3D input trajectory')

ax.legend()

ax.set_title('Traject13 20seconds 40pieces Mellinger')

plt.show()