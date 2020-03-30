import RPi.GPIO as gpio
import time
import requests
import json
import lcddriver

#Button configuration
BUTTON_LEFT         = 17
BUTTON_OK           = 27
BUTTON_RIGHT        = 22
BUTTON_BOUNCE_TIME  = 300

#Button callbacks
def button_pressed(channel):
    print(str(channel)+" pressed")

display = lcddriver.lcd()
display.lcd_display_string("Murge Machine", 1)

gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_LEFT, gpio.IN)
gpio.setup(BUTTON_OK, gpio.IN)
gpio.setup(BUTTON_RIGHT, gpio.IN)
gpio.add_event_detect(BUTTON_LEFT, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)
gpio.add_event_detect(BUTTON_OK, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)
gpio.add_event_detect(BUTTON_RIGHT, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)

cocktails=json.loads(requests.get("http://localhost:2636/cocktails").text)['cocktails']

for cocktail in cocktails:
    print(cocktail)

while(1):
    pass