#!/usr/bin/env python

import os
import time
import sys
import paho.mqtt.client as mqtt
import json

MQTT_BROKER='192.168.1.100'
MQTT_PORT=1883
MQTT_TOPIC='murgemachine'

def on_connect(client, userdata, flags, rc):
    print("Connected to "+MQTT_BROKER+" MQTT broker with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)
    print("Subscribed to topic "+MQTT_TOPIC)

def on_message(client, userdata, msg):
    msg_str=str(msg.payload.decode("utf-8","ignore"))
    msg_json=json.loads(msg_str)
    print(msg_str)
    client.disconnect()
    
client = mqtt.Client()
print("Connecting to "+MQTT_BROKER+" MQTT broker")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()