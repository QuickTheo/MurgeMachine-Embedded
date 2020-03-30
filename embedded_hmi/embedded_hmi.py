import RPi.GPIO as gpio
import time
import requests
import json
import lcddriver
import sys

#Button configuration
BUTTON_LEFT         = 17
BUTTON_OK           = 27
BUTTON_RIGHT        = 22
BUTTON_BOUNCE_TIME  = 300

#Button callbacks
def button_pressed(channel):
    print(str(channel)+" pressed")

display = lcddriver.lcd()

gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_LEFT, gpio.IN)
gpio.setup(BUTTON_OK, gpio.IN)
gpio.setup(BUTTON_RIGHT, gpio.IN)
gpio.add_event_detect(BUTTON_LEFT, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)
gpio.add_event_detect(BUTTON_OK, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)
gpio.add_event_detect(BUTTON_RIGHT, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)

try:
    cocktails=json.loads(requests.get("http://localhost:2636/cocktails").text)['cocktails']
except:
    display.lcd_display_string("Couldn't connect", 1)
    display.lcd_display_string("  to REST API   ", 2)
    sys.exit("Couldn't connect to REST API, exiting")

while(1):
    for cocktail in cocktails:
        print(cocktail['name'])
        display.lcd_clear()
        display.lcd_display_string(cocktail['name'],1)
        time.sleep(1)