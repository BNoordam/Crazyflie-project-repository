import numpy as np
import pandas as pd
import math

# Create an empty DataFrame to store the averages
result_list = []

data = pd.read_csv('OOI_traject19_log4_Robust_Mellinger_cf2.csv', header=0, delimiter=',', skiprows=0, usecols=[1, 2, 3, 4])
datalist = data.values.tolist()
# Convert figure8 to a NumPy array
data_array = np.array(datalist)

# Your data
x = data_array[:, 0]
y = data_array[:, 1]
z = data_array[:, 2]
yaw = data_array[:, 3]

Ref_data = pd.read_csv('timed_waypoints_yaw19.csv', header=0, delimiter=',', skiprows=0, usecols=[1, 2, 3, 4])
Ref_datalist = Ref_data.values.tolist()
# Convert figure8 to a NumPy array
Ref_data_array = np.array(Ref_datalist)

# Your data
Ref_x = Ref_data_array[:, 0]
Ref_y = Ref_data_array[:, 1]
Ref_z = Ref_data_array[:, 2]
#Ref_x = Ref_data_array[0:200, 0]
#Ref_y = Ref_data_array[0:200, 1]
#Ref_z = Ref_data_array[0:200, 2]


    

# Subtract the true x,y or z position, take the absolute value, and calculate the average
average_x = np.mean(np.abs(x-Ref_x))
average_y = np.mean(np.abs(y-Ref_y))
average_z = np.mean(np.abs(z-Ref_z))
#squared_x = np.square(average_x)
#squared_y = np.square(average_y)
#squared_z = np.square(average_z)
#squared_sum_xy = np.add(squared_x, squared_y)
#average_xy = np.sqrt(squared_sum_xy)
#squared_sum_xyz = np.add(squared_sum_xy, squared_z)
#average_xyz = np.sqrt(squared_sum_xyz)

# Append the averages to the DataFrame
#result_list.append({'X': true_x[i-1], 'Y': true_y[i-1],'Average_x': average_x, 'Average_y': average_y, 'Average_z': average_z, 'Average_xy': average_xy, 'Average_xyz': average_xyz})

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
print(f"Average of x: {average_x}")
print(f"Average of y: {average_y}")
print(f"Average of z: {average_z}")
print(f"MAE yaw: {average_yaw}")

result_df = pd.DataFrame(result_list)

# Write the DataFrame to a new CSV file
#result_df.to_csv('MAE_traject12_2.csv', index=False)


