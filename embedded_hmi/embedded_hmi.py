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
viewNumber=1
cocktails={}

lcd.lcd_init()
lcd.lcd_string(" Murge Machine ", 0x80)
lcd.lcd_string("      v0.1     ", 0x8C0)
time.sleep(5)

lcd.lcd_init()
lcd.lcd_string("   Waiting for     ", 0x80)
lcd.lcd_string("   REST API...     ", 0x8C0)

def refresh_cocktail_list():
    global cocktails
    print("Attempting to connect to REST API...")
    try:
        return json.loads(requests.get("http://localhost:2636/cocktails").text)['cocktails']
    except:
        return 0

while len(cocktails)==0:
    cocktails=refresh_cocktail_list()
    time.sleep(1)

#Button callbacks
def button_pressed(channel):
    global ignore_presses
    global viewNumber

    cocktails=refresh_cocktail_list()

    if(ignore_presses==0 & cocktails!=0):
        print(str(channel)+" pressed")
        global currentCocktailArrayId
        ignore_presses=1

        if viewNumber==1 :
            if channel==17:
                if(currentCocktailArrayId==0):
                    currentCocktailArrayId=len(cocktails)-1
                else:
                    currentCocktailArrayId-=1
                refresh_screen()
            elif channel==27:
                select_cocktail_size()
            elif channel==22:
                if (currentCocktailArrayId+1)==len(cocktails):
                    currentCocktailArrayId=0
                else:
                    currentCocktailArrayId+=1
                refresh_screen()
        elif viewNumber==2:
            if channel==17:
                print("Sending preparation order to REST API for 25cl of "+cocktails[currentCocktailArrayId]['name'])
            elif channel==22:
                print("Sending preparation order to REST API for 50cl of "+cocktails[currentCocktailArrayId]['name'])

            viewNumber=1
            refresh_screen()
            
        ignore_presses=0

def refresh_screen():
    global currentCocktailArrayId
    lcd.lcd_init()
    lcd.lcd_string(cocktails[currentCocktailArrayId]['name'], 0x80)
    lcd.lcd_string("<      o       >", 0x8C0)

def select_cocktail_size():
    global currentCocktailArrayId
    global viewNumber

    viewNumber=2
    lcd.lcd_init()
    lcd.lcd_string("    Taille?     ", 0x80)
    lcd.lcd_string("25     <      50", 0x8C0)

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