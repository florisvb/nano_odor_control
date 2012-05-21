// nano_ssr_firmware.pde 
//
// Basic firmware for IO Rodeo's solid state relay exapansion board for the
// Arduino Nano. Enables users to set the values of the relay uisng serial
// communications.  
//
// Requires the  SerialReceiver library from the
// iorodeo_arduino_libs http://bitbucket.org/iorodeo/iorodeo_arduino_libs.
// and the Streaming library http://arduiniana.org/2009/04/new-streaming-library/
//
// Author: Will Dickson, IO Rodeo Inc.
// 
// ----------------------------------------------------------------------------
#include "Streaming.h"
#include "SerialReceiver.h"

// Global variables
const uint8_t numSSR = 8;
const uint8_t ssrPin[numSSR] = {2,3,4,5,6,7,8,9};
const uint8_t ainPin = 6;

SerialReceiver receiver;

unsigned long time_now;
unsigned long time_start;
unsigned long time_prev_pulse;
unsigned long time_done;

unsigned long recording_delay;

unsigned long pulse_length;
unsigned long pulse_interval;
unsigned long exp_length;

bool record_data;
bool record_flag;
bool ssr_state;
uint16_t ssr_num;

uint16_t num_pulses;
uint16_t num_pulsed;

int sample_value;


// Function prototypes

void set_variables() {
    time_now = 0;
    time_start = 0;
    time_prev_pulse = 0;
    
    pulse_length = 0;
    pulse_interval = 0;
    exp_length = 0;
    
    record_data = 0;
    record_flag = 0;
    ssr_state = 0;
    ssr_num = 0;
    
    recording_delay = 30000;

}



// System initialization
void setup() {
    set_variables();

    Serial.begin(115200);
    
    // Set SSR pins to output and set to low
    for (uint8_t i=0; i<numSSR; i++) {
        pinMode(ssrPin[i], OUTPUT);
        digitalWrite(ssrPin[i],LOW);
    }
}



// Main loop
void loop() {

    time_now = millis();
    
    if (time_now < time_start + exp_length) {
        if ((ssr_state == 0) && (time_now > time_prev_pulse + pulse_length + pulse_interval)) {
            digitalWrite(ssrPin[ssr_num], 1);
            time_prev_pulse = time_now;
            ssr_state = 1;
            
        } 
        
        
        
        if ((ssr_state == 1) && (time_now > time_prev_pulse + pulse_length)) {
            digitalWrite(ssrPin[ssr_num], 0);
            ssr_state = 0;
            time_done = time_now - time_start;
        } 
        
    }
        
        
    if (time_now > time_start + exp_length) {
      
        if (ssr_state == 1) {
          digitalWrite(ssrPin[ssr_num], 0);
          ssr_state = 0;
          time_done = time_now - time_start;
        }
        
        if (time_now > time_start + exp_length + recording_delay) {
          record_flag = 0;
          if (record_data) {
            Serial << "done" << endl;
          }
          set_variables();
        }
    
    }
     
    
      
    //sample_num = (time_now-time_start_recording)/sample_period;
    //if ((record_flag) && (sample_num>last_sample_num)) {
    if (record_flag) {
        sample_value = analogRead(ainPin);
        //Serial << ssr_state << "," << micros() << "," << sample_value << endl;
        //Serial << time_now << "," << time_start << "," << exp_length << endl;
        //last_sample_num = sample_num;
    }
    
    //if (record_flag == 0) {
    if (1) {  
      while (Serial.available() > 0) {
            receiver.process(Serial.read());
            if (receiver.messageReady()) {
                ssr_num = receiver.readInt(0);
                pulse_length = receiver.readInt(1);
                pulse_interval = receiver.readInt(2);
                exp_length = receiver.readInt(3);
                record_data = receiver.readInt(4);
                
                time_start = millis();
                time_prev_pulse = time_start;
                
                
                    
                if (pulse_length > 0) {
                    if (record_data) {
                      record_flag = 1;
                    }
                }
                receiver.reset();
                
                
                Serial << time_now << "," << time_start << "," << exp_length << endl;
            }
        }
    }
}



