#!/usr/bin/env python

import board
import os
import time
import sys
import paho.mqtt.client as mqtt
import json
import threading
import RPi.GPIO as gpio
import array
from LEDStrip import CustomLEDStrip

class Actuator(mqtt.Client):
    def __init__(self, mqtt_broker, mqtt_topic, pump_connections, pump_ratio, *args, **kwargs):
        super(Actuator, self).__init__(*args, **kwargs)
        self.strip=CustomLEDStrip(21)
        self.strip.set_idle_light_config(json.dumps('{"light" : {"color" : "#ff0000","effect" : "fixed"} }'))
        self.pumps=pump_connections
        self.pump_ratio=pump_ratio
        self.init_pumps()
        self.mqtt_broker=mqtt_broker
        self.mqtt_topic=mqtt_topic
        self.run()

    def __del__(self):
        gpio.cleanup()

    def init_pumps(self):
        print("Configuring pumps...")
        for pump in self.pumps:
            gpio.setup(pump, gpio.OUT)
            gpio.output(pump, gpio.HIGH)
    
    def turn_on_pump(self, pump_no, s):
        print("Turning on pump "+str(pump_no)+" for "+str(s)+" seconds")
        gpio.output(self.pumps[int(pump_no)-1], gpio.LOW)
        time.sleep(float(s))
        print("Turning off pump "+str(pump_no))
        gpio.output(self.pumps[int(pump_no)-1], gpio.HIGH)

    def on_connect(self, mqttc, obj, flags, rc):
        if(rc==0):
            print("Connected to MQTT broker at "+self.mqtt_broker)
        else:
            sys.exit("Couldn't connect to MQTT broker at "+self.mqtt_broker+", exiting")

    def on_message(self, mqttc, obj, msg):
        print("Cocktail payload received on topic "+msg.topic)
        data=json.loads(str(msg.payload.decode()))
        light=data['light']
        light_animation_time=self.pump_ratio*100*int(data['preparation']['size'])/25

        if str(light['effect'])=="fixed":
            self.strip.set_fixed_color_threaded(str(light['color']))
        elif str(light['effect'])=="rainbow":
            pass
        elif str(light['effect'])=="fade":
            pass
        elif str(light['effect'])=="flash":
            pass
        elif str(light['effect'])=="chase":
            #self.strip.set_chasing_color_threaded(str(light['color']), light_animation_time)
            pass

        for pump in data['preparation']['pumpsActivation']:
            self.turn_on_pump(int(pump['number']), self.pump_ratio*float(pump['part'])*int(data['preparation']['size'])/25)

        self.strip.reset_idle_light_config()

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed to topic "+self.mqtt_topic)

    def run(self):
        self.connect(self.mqtt_broker, 1883, 60)
        self.subscribe(self.mqtt_topic)
        self.loop_forever()

    def test_all_pumps(self):
        print("Testing all "+str(len(self.pumps))+" pumps")
        for i in range(1, len(self.pumps)+1):
            self.turn_on_pump(i, 3)


if __name__ == "__main__":
    actuator=None
    try:
        actuator=Actuator("192.168.1.100", "murgemachine", [13, 19, 26, 16, 20, 21], 0.1)
    except:
        del actuator