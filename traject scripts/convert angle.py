import numpy as np
import pandas as pd
import math

data = pd.read_csv('traject12_log4C_Robust_Mellinger_cf8.csv', header=0, delimiter=',', skiprows=0, usecols=[1, 2, 3, 4])
datalist = data.values.tolist()
# Convert figure8 to a NumPy array
data_array = np.array(datalist)

# Your data
x = data_array[:, 0]
y = data_array[:, 1]
z = data_array[:, 2]
yaw = data_array[:, 3]

Ref_data = pd.read_csv('timed_waypoints_yaw12.csv', header=0, delimiter=',', skiprows=0, usecols=[1, 2, 3, 4])
Ref_datalist = Ref_data.values.tolist()
# Convert figure8 to a NumPy array
Ref_data_array = np.array(Ref_datalist)

Ref_yaw = Ref_data_array[:, 3]/math.pi*180


# Function to convert degrees to the desired format
def convert_degrees(degrees):
    # Convert to range [0, 360)
    degrees %= 360
    
    # Convert to the desired format
    if degrees <= 180:
        return degrees
    else:
        return degrees - 360

# Apply the conversion function to each element in the dataset
converted_data = np.vectorize(convert_degrees)(Ref_yaw)

average_yaw = np.mean(np.abs(yaw-converted_data))

# Print the result
print(f"MAE yaw: {average_yaw}")