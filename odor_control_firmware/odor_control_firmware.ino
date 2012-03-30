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
const uint8_t ainPin = 0;

SerialReceiver receiver;

unsigned long time_now;
uint8_t sample_period; //in ms
unsigned long sample_num;
unsigned long last_sample_num;
int sample_value;
uint16_t pulse;
uint16_t ssr_num;
bool ssr_state;
bool record_flag;
unsigned int pulse_delay;
unsigned int record_after_pulse;
unsigned int time_start_recording;

// Function prototypes
void handleMessage(uint16_t cmdNum, uint16_t cmdVal);

// System initialization
void setup() {
    sample_num = 0;
    last_sample_num = 0;
    time_now = 0;
    pulse = 0;
    record_flag = 0;
    ssr_state = 0;
    
    sample_period = 2;
    pulse_delay = 1000;
    record_after_pulse = 5000;

    Serial.begin(9600);
    // Set SSR pins to output and set to low
    for (uint8_t i=0; i<numSSR; i++) {
        pinMode(ssrPin[i], OUTPUT);
        digitalWrite(ssrPin[i],LOW);
    }
}

// Main loop
void loop() {

    time_now = millis();
    
    if (record_flag) {
        if ((ssr_state == 0) && (time_now > time_start_recording + pulse_delay)) {
            digitalWrite(ssrPin[ssr_num], 1);
            ssr_state = 1;
        }
        
        if ((ssr_state == 1) && (time_now > time_start_recording + pulse_delay + pulse)) {
            digitalWrite(ssrPin[ssr_num], 0);
            ssr_state = 0;
        }
        
        if (time_now > time_start_recording + pulse_delay + pulse + record_after_pulse) {
            record_flag = 0;
            Serial << "done" << endl;
        }
    }
      
    sample_num = time_now/sample_period;
    if ((record_flag) && (sample_num>last_sample_num)) {
        sample_value = analogRead(ainPin);
        Serial << ssr_state << "," << sample_num << "," << time_now << "," << sample_value << endl;
    }
    
    while (Serial.available() > 0) {
        receiver.process(Serial.read());
        if (receiver.messageReady()) {
            ssr_num = receiver.readInt(0);
            pulse = receiver.readInt(1);
            
            if (pulse > 0) {
                record_flag = 1;
                time_start_recording = millis();
            }
            receiver.reset();
        }
    }
}



