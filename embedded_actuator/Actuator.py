#!/usr/bin/env python

import board
import os
import time
import sys
import paho.mqtt.client as mqtt
import json
import neopixel
import threading
import RPi.GPIO as gpio
import array

class Actuator(mqtt.Client):
    def __init__(self, mqtt_broker, mqtt_topic, pump_connections, pump_ratio, *args, **kwargs):
        super(Actuator, self).__init__(*args, **kwargs)
        self.pumps=pump_connections
        self.pump_ratio=pump_ratio
        self.init_pumps()
        self.mqtt_broker=mqtt_broker
        self.mqtt_topic=mqtt_topic
        self.run()

    def init_pumps(self):
        print("Configuring pumps...")
        for pump in self.pumps:
            gpio.setup(pump, gpio.OUT)
            gpio.output(pump, gpio.HIGH)
    
    def turn_on_pump(self, pump_no, s):
        print("Turning on pump "+str(pump_no)+" for "+str(s)+" seconds")
        gpio.output(self.pumps[int(pump_no)-1], gpio.LOW)
        timer=threading.Timer(float(s), turn_off_pump, [int(pump_no)])
        timer.start()

    #Pump off function
    def turn_off_pump(self, pump_no):
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

        for i in range(0, data['preparation']['size']):
            for pump in data['preparation']['pumpsActivation']:
                turn_on_pump(int(pump['number']), float(pump['part'])*self.pump_ratio)

            light=data['light']
            if str(light['effect'])=="fixed":
                strip.fill(tuple(int(((str(light['color'])).lstrip('#'))[i:i+2], 16) for i in (0, 2, 4)))
            elif str(light['effect'])=="rainbow":
                pass
            elif str(light['effect'])=="fade":
                pass
            elif str(light['effect'])=="flash":
                pass
            elif str(light['effect'])=="chase":
                for i in range(0, LED_COUNT):
                    strip[i]=tuple(int(((str(light['color'])).lstrip('#'))[i:i+2], 16) for i in (0, 2, 4))
                    time.sleep(0.01)
                for i in range(0, LED_COUNT):
                    strip[i]=(0,0,0)
                    time.sleep(0.01)

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed to topic "+self.mqtt_topic)

    def run(self):
        self.connect(self.mqtt_broker, 1883, 60)
        self.subscribe(self.mqtt_topic)
        self.loop_forever()


if __name__ == "__main__":
    actuator=Actuator("192.168.1.100", "murgemachine", [13, 19, 26, 16, 20, 21], 0.1)