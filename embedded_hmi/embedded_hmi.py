import RPi.GPIO as gpio
import time
import requests
import json
import lcd_i2c as lcd
import sys

#Button configuration
BUTTON_LEFT         = 17
BUTTON_OK           = 27
BUTTON_RIGHT        = 22
BUTTON_BOUNCE_TIME  = 300
ignore_presses      = 0

currentCocktailArrayId=0

try:
    cocktails=json.loads(requests.get("http://localhost:2636/cocktails").text)['cocktails']
except:
    display.lcd_display_string("Couldn't connect", 1)
    display.lcd_display_string("  to REST API   ", 2)
    sys.exit("Couldn't connect to REST API, exiting")

#Button callbacks
def button_pressed(channel):
    global ignore_presses

    if(ignore_presses==0):
        print(str(channel)+" pressed")
        global currentCocktailArrayId
        ignore_presses=1

        if channel==17:
            if(currentCocktailArrayId==0):
                currentCocktailArrayId=len(cocktails)-1
            else:
                currentCocktailArrayId-=1
            refresh_screen()
        elif channel==27:
            print("Sending preparation order to REST API for \""+cocktails[currentCocktailArrayId]['name']+"\"")
        elif channel==22:
            if((currentCocktailArrayId+1)==len(cocktails)):
                currentCocktailArrayId=0
            else:
                currentCocktailArrayId+=1
            refresh_screen()
            
        ignore_presses=0

def refresh_screen():
    global currentCocktailArrayId
    lcd.lcd_init()
    lcd.lcd_string(cocktails[currentCocktailArrayId]['name'], 0x80)
    lcd.lcd_string("<      o       >", 0x8C0)

lcd.lcd_init()

gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_LEFT, gpio.IN)
gpio.setup(BUTTON_OK, gpio.IN)
gpio.setup(BUTTON_RIGHT, gpio.IN)
gpio.add_event_detect(BUTTON_LEFT, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)
gpio.add_event_detect(BUTTON_OK, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)
gpio.add_event_detect(BUTTON_RIGHT, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)

refresh_screen()

while(1):
    pass