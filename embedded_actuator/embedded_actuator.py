#!/usr/bin/env python

import board
import os
import time
import sys
import paho.mqtt.client as mqtt
import json
from neopixel import *

#MQTT constants
MQTT_BROKER     = '192.168.1.100'
MQTT_PORT       = 1883
MQTT_TOPIC      = 'murgemachine'

#WS2812 LED strip constants
LED_COUNT      = 21      # Number of LED pixels.

#MQTT connect callback
def on_connect(client, userdata, flags, rc):
    print("Connected to "+MQTT_BROKER+" MQTT broker with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)
    print("Subscribed to topic "+MQTT_TOPIC)

#MQTT on message received callback
def on_message(client, userdata, msg):
    msg_json=json.loads(msg.payload.decode())
    strip=neopixel.NeoPixel(board.D12,LED_COUNT) 

    for x in range(0, LED_COUNT):
        strip[x] = (255, 0, 0)
        sleep(1)

client = mqtt.Client()
print("Connecting to "+MQTT_BROKER+" MQTT broker")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()