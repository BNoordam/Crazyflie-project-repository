# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2018 Bitcraze AB
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
Simple example that connects to one crazyflie (check the address at the top
and update it to your crazyflie address) and uses the high level commander
to send setpoints and trajectory to fly a figure 8.

This example is intended to work with any positioning system (including LPS).
It aims at documenting how to set the Crazyflie in position control mode
and how to send setpoints using the high level commander.
"""
import sys
import time


import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.mem import MemoryElement
from cflib.crazyflie.mem import Poly4D
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.utils import uri_helper
import pandas as pd

import os

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/1/2M/E7E7E7E7E7')

# The trajectory to fly
# See https://github.com/whoenig/uav_trajectories for a tool to generate
# trajectories

# /home/Bjorn/aideck-gap8-examples/examples/other/wifi-img-streamer/

# Duration,x^0,x^1,x^2,x^3,x^4,x^5,x^6,x^7,y^0,y^1,y^2,y^3,y^4,y^5,y^6,y^7,z^0,z^1,z^2,z^3,z^4,z^5,z^6,z^7,yaw^0,yaw^1,yaw^2,yaw^3,yaw^4,yaw^5,yaw^6,yaw^7
# Read the CSV file with manual header and delimiter specification
data = pd.read_csv("yaw14.csv", header=None, delimiter=',', skiprows=1)

# Convert the DataFrame to a list of lists
figure8 = data.values.tolist()




def wait_for_position_estimator(scf):
    print('Waiting for estimator to find position...')

    log_config = LogConfig(name='Kalman Variance', period_in_ms=10)
    log_config.add_variable('kalman.varPX', 'float')
    log_config.add_variable('kalman.varPY', 'float')
    log_config.add_variable('kalman.varPZ', 'float')

    var_y_history = [1000] * 10
    var_x_history = [1000] * 10
    var_z_history = [1000] * 10

    threshold = 0.001

    with SyncLogger(scf, log_config) as logger:
        for log_entry in logger:
            data = log_entry[1]

            var_x_history.append(data['kalman.varPX'])
            var_x_history.pop(0)
            var_y_history.append(data['kalman.varPY'])
            var_y_history.pop(0)
            var_z_history.append(data['kalman.varPZ'])
            var_z_history.pop(0)

            min_x = min(var_x_history)
            max_x = max(var_x_history)
            min_y = min(var_y_history)
            max_y = max(var_y_history)
            min_z = min(var_z_history)
            max_z = max(var_z_history)

            #print("{} {} {}".
                #format(max_x - min_x, max_y - min_y, max_z - min_z))

            if (max_x - min_x) < threshold and (
                    max_y - min_y) < threshold and (
                    max_z - min_z) < threshold:
                break


def reset_estimator(cf):
    cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    cf.param.set_value('kalman.resetEstimation', '0')

    wait_for_position_estimator(cf)


def activate_PID_controller(cf):
    cf.param.set_value('stabilizer.controller', '1')

def activate_INDI_controller(cf):
    cf.param.set_value('stabilizer.controller', '3')

def activate_Brescianini_controller(cf):
    cf.param.set_value('stabilizer.controller', '4')

def activate_mellinger_controller(cf):
    cf.param.set_value('stabilizer.controller', '2')

def activate_robust_tdoa(cf):
    cf.param.set_value('kalman.robustTdoa', '1')

def deactivate_robust_tdoa(cf):
    cf.param.set_value('kalman.robustTdoa', '0')


def upload_trajectory(cf, trajectory_id, trajectory):
    trajectory_mem = cf.mem.get_mems(MemoryElement.TYPE_TRAJ)[0]
    trajectory_mem.trajectory = []

    total_duration = 0
    for row in trajectory:
        duration = row[0]
        print(duration)
        x = Poly4D.Poly(row[1:9])
        y = Poly4D.Poly(row[9:17])
        z = Poly4D.Poly(row[17:25])
        yaw = Poly4D.Poly(row[25:33])
        trajectory_mem.trajectory.append(Poly4D(duration, x, y, z, yaw))
        total_duration += duration

    upload_result = trajectory_mem.write_data_sync()
    if not upload_result:
        print('Upload failed, aborting!')
        sys.exit(1)
    cf.high_level_commander.define_trajectory(trajectory_id, 0, len(trajectory_mem.trajectory))
    return total_duration


def run_sequence(cf, trajectory_id, duration):
    commander = cf.high_level_commander

    commander.takeoff(0.25, 3.0)
    time.sleep(3.0)
    relative = False
    commander.start_trajectory(trajectory_id, 1.0, relative)
    time.sleep(duration)
    commander.land(0.0, 2.0)
    time.sleep(2)
    commander.stop()

def position_callback(timestamp, data, logconf):
    x = data['kalman.stateX']
    y = data['kalman.stateY']
    z = data['kalman.stateZ']
    # print('pos: ({}, {}, {})'.format(x, y, z))

    file_path = 'traject14_log_Robust_Mellinger_cf2.csv'
    file_exists = os.path.exists(file_path)

    # Write headers only if the file doesn't exist
    with open(file_path, 'a', newline='') as file:
        df = pd.DataFrame({'timestamp': [timestamp], 'Kalman.stateX': [x], 'Kalman.stateY': [y], 'Kalman.stateZ': [z]})
        df.to_csv(file, index=False, header=not file_exists, mode='a')


def start_position_printing(scf):
    log_conf = LogConfig(name='Kalman', period_in_ms=100)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()

def video_streaming():
    exec(open("opencv_viewer.py").read())  

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf
        trajectory_id = 1

        # CHOOSE A CONTROLLER
        activate_mellinger_controller(cf)
        #activate_INDI_controller(cf)
        #activate_PID_controller(cf)
        #activate_Brescianini_controller(cf)

        # USE ROBUST TDOA OR NOT 
        activate_robust_tdoa(cf)
        #deactivate_robust_tdoa(cf)
        
        
        duration = upload_trajectory(cf, trajectory_id, figure8)
        print('The sequence is {:.1f} seconds long'.format(duration))        
        reset_estimator(cf)
        start_position_printing(scf)
        #thread_one = threading.Thread(target=run_sequence(cf, trajectory_id, duration))
        #thread_two = threading.Thread(target=video_streaming)
        #thread_one.start()
        #thread_two.start()
        run_sequence(cf, trajectory_id, duration)
