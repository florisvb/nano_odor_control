#!/usr/bin/env python
import roslib; roslib.load_manifest('ros_flydra')
import rospy
from ros_flydra.srv import *
import time

"""
Python serial interface to the IO Rodeo solid state relay expansion board for 
the Arduino Nano. 

Author: Will Dickson, IO Rodeo Inc.

Copyright 2010  IO Rodeo Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import serial
import numpy as np

import odor_dataset as od
from odor_dataset import *

class BasicSSR(serial.Serial):

    def __init__(self,**kwargs):
        super(BasicSSR,self).__init__(**kwargs)
           
    def pulse(self, ssr_num, pulse_length, pulse_interval, num_pulses, exp_length, record_data):
        self.write('[%d, %d, %d, %d, %d]\n'%(ssr_num, pulse_length, pulse_interval, exp_length, record_data))
        
    def listen(self):
        raw_data = []
        do_work = 1
        
        print 'recording data!'
        while do_work:
            data = self.readline()
            print data
            if 'done' in data:
                do_work = 0
            else:
                raw_data.append(data)
        print 'done recording data!'
        return raw_data
        
    def process_raw_data(self, raw_data):
        print 'parsing'
        
        data_arr_tmp = np.zeros([len(raw_data), 3])
        for i, data in enumerate(raw_data):
            if data != 'done':
                data_split = data.split(',')
                # Serial << ssr_state << "," << sample_num << "," << time_now << "," << sample_value << endl;
                for j, d in enumerate(data_split):
                    data_arr_tmp[i, j] = data_split[j]
        
        odor_data = OdorData()
        odor_data.odortrace = data_arr_tmp[:,0]
        try:
            odor_on_index = np.where(np.diff(odor_data.odortrace)==1)[0][0]
        except:
            odor_on_index = np.where(np.diff(odor_data.odortrace)==1)[0]
        odor_data.odor_on_index = odor_on_index
        
        #odor_data.sample_num = data_arr_tmp[:,1]
        odor_data.time = data_arr_tmp[:,1] - data_arr_tmp[odor_data.odor_on_index,1]
        odor_data.voltage = data_arr_tmp[:,2]
        
        print 'done parsing'
        
        return odor_data
        
    def run_experiment(self, pulse_length, pulse_interval, num_pulses, exp_length, record_data):
        self.pulse(0, pulse_length, pulse_interval, num_pulses, exp_length, record_data)
        raw_data = self.listen()
        odor_data = self.process_raw_data(raw_data)
        
        return odor_data


class Flydra_Service_Listener:
    def __init__(self):
        rospy.wait_for_service("flydra_super_packet_service")
        self.get_latest_flydra_data = rospy.ServiceProxy("flydra_super_packet_service", super_packet_service)

    def get_position_from_flydra_data(self):
        superpacket = self.get_latest_flydra_data().packets
        for packet in superpacket.packets:
            if len(packet.objects) == 1:
                for obj in packet.objects:
                    position = [obj.position.x, obj.position.y, obj.position.z]
                    return position             

    def get_mean_led_position(self, n_avg=20):
        positions = None
        n = 0
        while n<n_avg:
            position = self.get_position_from_flydra_data()
            if positions is None:
                positions = np.array(position)
            else:
                positions = np.vstack((positions, position))
            n+=1
        positions_avg = np.mean(positions, axis=0)
        return positions_avg
    
def run_experiment(filename='odor_dataset', pulse_length=100, pulse_interval=100, num_pulses=10, exp_length=10000, record_data=1, odor_type=None, resistance=None, num_trials=1, gain=1):
    if filename == 'odor_dataset':
        try:
            odor_dataset = od.load(filename)
        except:
            odor_dataset = od.OdorDataset()
    else:
        odor_dataset = od.OdorDataset()
        
    try:
        new_experiment_key = odor_dataset.experiments.keys()[-1] + 1
    except:
        new_experiment_key = 0
        
    experiment = OdorExperiment(pulse_length, odor_type)
    
    for n in range(num_trials):
        print 'running trial # ', n, ' out of ', num_trials
        trial = run_trial(pulse_length, pulse_interval, num_pulses, exp_length, record_data, resistance, gain)
        try:
            new_key = experiment.trials.keys()[-1] + 1
        except:
            new_key = 0
        experiment.trials.setdefault(new_key, trial)
        
    odor_dataset.experiments.setdefault(new_experiment_key, experiment)
    save(odor_dataset, filename)
    print 'experiment data saved'
    
    return
            
        
        
def run_trial(pulse_length, pulse_interval, num_pulses, exp_length, record_data, resistance=None, gain=1):

    dev = BasicSSR(port='/dev/ttyUSB0',timeout=1, baudrate=115200)
    time.sleep(2.0) # Sleep for serial reset of arduino
    data = dev.run_experiment(pulse_length, pulse_interval, num_pulses, exp_length, record_data)

    # get flydra data    
    print 'getting flydra data'
    fsl = Flydra_Service_Listener()
    position = fsl.get_mean_led_position()
    print 'got flydra data: ', position
    
    new_trial = OdorTrial(position, data.time, data.odortrace, data.odor_on_index, data.voltage, resistance, gain)
    return new_trial
            
        
        

'''    

d_mm = 3.15
d = d_mm/1000.
r = d/2.
area = np.pi*r**2
wind_speed = .4
flow_rate = area*wind_speed
flow_rate_sccs = flow_rate*100**3
flow_rate_sccm = flow_rate_sccs * 60.

yield: 187 sccm
'''








if __name__ == '__main__':
    run_experiment(filename='odor_dataset', pulse_length=250, pulse_interval=3000, num_pulses=0, exp_length=32780, record_data=1, odor_type='acetone', resistance=100, num_trials=1, gain=1)
    
    print 'done'







