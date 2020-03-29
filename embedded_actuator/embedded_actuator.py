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

#MQTT constants
MQTT_BROKER     = '192.168.1.100'
MQTT_PORT       = 1883
MQTT_TOPIC      = 'murgemachine'

#WS2812 LED strip constants
LED_COUNT       = 21      # Number of LED pixels.

#Pumps
PUMPS           = [13, 19, 26, 16, 20, 21]

#Pump on function
def turn_on_pump(pump_no, s):
    print("Turning on pump "+str(pump_no))
    gpio.output(PUMPS[int(pump_no-1)], gpio.LOW)
    timer=threading.Timer(s, turn_off_pump, [pump_no])
    timer.start()

#Pump off function
def turn_off_pump(pump_no):
    print("Turning off pump "+str(pump_no))
    gpio.output(PUMPS[pump_no-1], gpio.HIGH)

#MQTT connect callback
def on_connect(client, userdata, flags, rc):
    print("Connected to "+MQTT_BROKER+" MQTT broker with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)
    print("Subscribed to topic "+MQTT_TOPIC)

#MQTT on message received callback
def on_message(client, userdata, msg):
    print("Cocktail payload received")
    #msg_json=json.loads(msg.payload.decode())
    strip=neopixel.NeoPixel(board.D18,LED_COUNT)
    turn_on_pump(5, 3)
    turn_on_pump(6, 6)
    #strip[i]=(255,255,255)

#Pump configuration
gpio.setup(PUMPS[0], gpio.OUT)
gpio.setup(PUMPS[1], gpio.OUT)
gpio.setup(PUMPS[2], gpio.OUT)
gpio.setup(PUMPS[3], gpio.OUT)
gpio.setup(PUMPS[4], gpio.OUT)
gpio.setup(PUMPS[5], gpio.OUT)
gpio.output(PUMPS[0], gpio.HIGH)
gpio.output(PUMPS[1], gpio.HIGH)
gpio.output(PUMPS[2], gpio.HIGH)
gpio.output(PUMPS[3], gpio.HIGH)
gpio.output(PUMPS[4], gpio.HIGH)
gpio.output(PUMPS[5], gpio.HIGH)

#MQTT configuration
client = mqtt.Client()
print("Connecting to "+MQTT_BROKER+" MQTT broker")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.on_connect = on_connect
client.on_message = on_message
client.loop_forever()