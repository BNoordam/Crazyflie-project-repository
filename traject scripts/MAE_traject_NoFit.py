import numpy as np
import pandas as pd


i=1
iter=46

true_x=np.array([0.5,1,1.5,2,2.5]+[0,0.5,1,1.5,2,2.5]*6+[0.5,1,1.5,2,2.5])
true_y=np.array([0]*5+[0.5]*6+[1]*6+[1.5]*6+[2]*6+[2.5]*6+[3]*6+[3.5]*5)

# Create an empty DataFrame to store the averages
result_list = []

data_pre = pd.read_csv('traject11_log2_Robust_PID_cf2.csv', header=0, delimiter=',', skiprows=0, usecols=[1, 2, 3])
data = data_pre.iloc[35:236, :]
datalist = data.values.tolist()
# Convert figure8 to a NumPy array
data_array = np.array(datalist)

# Your data
x = data_array[:, 0]
y = data_array[:, 1]
z = data_array[:, 2]

Ref_data = pd.read_csv('timed_waypoints_yaw11.csv', header=0, delimiter=',', skiprows=0, usecols=[1, 2, 3])
Ref_datalist = Ref_data.values.tolist()
# Convert figure8 to a NumPy array
Ref_data_array = np.array(Ref_datalist)

# Your data
Ref_x = Ref_data_array[:, 0]
Ref_y = Ref_data_array[:, 1]
Ref_z = Ref_data_array[:, 2]


    

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

print(f"Average of x: {average_x}")
print(f"Average of y: {average_y}")
print(f"Average of z: {average_z}")

result_df = pd.DataFrame(result_list)

# Write the DataFrame to a new CSV file
#result_df.to_csv('MAE_traject12_2.csv', index=False)


