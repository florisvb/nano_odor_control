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
import pickle

class BasicSSR(serial.Serial):

    def __init__(self,**kwargs):
        super(BasicSSR,self).__init__(**kwargs)
           
    def pulse(self, ssr_num, pulse_length):
        self.write('[%d, %d]\n'%(ssr_num, pulse_length))
        
    def listen(self):
        raw_data = []
        do_work = 1
        
        while do_work:
            data = self.readline()
            print data
            
            if data == 'done':
                do_work = 0
            else:
                raw_data.append(data)
                
        return raw_data
        
    def process_raw_data(self, raw_data):
        print 'parsing'
        return
        
    def run_experiment(self, pulse):
        
        self.pulse(1, pulse)
        raw_data = listen()
        processed_data = self.process_raw_data(raw_data)
        
        
        
        
        
            
            
        


