#!/usr/bin/python

import RPi.GPIO as gpio
import time
import requests
import json
import lcd_i2c as lcd
import sys

BUTTON_LEFT         = 17
BUTTON_CENTER       = 27
BUTTON_RIGHT        = 22
BUTTON_BOUNCE_TIME  = 300

class HMI:
    def __init__(self, api_addr):
        self.api_addr=api_addr

        gpio.setmode(gpio.BCM)
        gpio.setup(BUTTON_LEFT, gpio.IN)
        gpio.setup(BUTTON_CENTER, gpio.IN)
        gpio.setup(BUTTON_RIGHT, gpio.IN)
        gpio.add_event_detect(BUTTON_LEFT, gpio.FALLING, callback=self.cocktail_navigation_callback, bouncetime=BUTTON_BOUNCE_TIME)
        gpio.add_event_detect(BUTTON_CENTER, gpio.FALLING, callback=self.cocktail_navigation_callback, bouncetime=BUTTON_BOUNCE_TIME)
        gpio.add_event_detect(BUTTON_RIGHT, gpio.FALLING, callback=self.cocktail_navigation_callback, bouncetime=BUTTON_BOUNCE_TIME)

        self.ignore_button_presses=0
        self.refresh_cocktail_list()
        self.position=0
        self.refresh_screen()

    def __del__(self):
        lcd.lcd_init()
        gpio.cleanup()

    def cocktail_navigation_callback(self, button):
        if self.ignore_button_presses==0:
            self.ignore_button_presses=1
            if button==BUTTON_LEFT:
                print("LEFT")
                if self.position==0:
                    self.position=len(self.cocktails)-1
                else:
                    self.position-=1
                self.refresh_screen()
            elif button==BUTTON_CENTER:
                print("OK")
                gpio.remove_event_detect(BUTTON_LEFT)
                gpio.remove_event_detect(BUTTON_CENTER)
                gpio.remove_event_detect(BUTTON_RIGHT)
                gpio.add_event_detect(BUTTON_LEFT, gpio.FALLING, callback=self.cocktail_size_select_callback, bouncetime=BUTTON_BOUNCE_TIME)
                gpio.add_event_detect(BUTTON_CENTER, gpio.FALLING, callback=self.cocktail_size_select_callback, bouncetime=BUTTON_BOUNCE_TIME)
                gpio.add_event_detect(BUTTON_RIGHT, gpio.FALLING, callback=self.cocktail_size_select_callback, bouncetime=BUTTON_BOUNCE_TIME)
                self.display_cocktail_size_choice()
            elif button==BUTTON_RIGHT:
                print("RIGHT")
                if self.position==len(self.cocktails)-1:
                    self.position=0
                else:
                    self.position+=1
                self.refresh_screen()
            self.ignore_button_presses=0

    def cocktail_size_select_callback(self, button):
        if self.ignore_button_presses==0:
            self.ignore_button_presses=1
            if button==BUTTON_LEFT:
                print("25cl")
            elif button==BUTTON_CENTER:
                print("back")
            elif button==BUTTON_RIGHT:
                print("50cl")
            self.refresh_screen()
            gpio.remove_event_detect(BUTTON_LEFT)
            gpio.remove_event_detect(BUTTON_CENTER)
            gpio.remove_event_detect(BUTTON_RIGHT)
            gpio.add_event_detect(BUTTON_LEFT, gpio.FALLING, callback=self.cocktail_navigation_callback, bouncetime=BUTTON_BOUNCE_TIME)
            gpio.add_event_detect(BUTTON_CENTER, gpio.FALLING, callback=self.cocktail_navigation_callback, bouncetime=BUTTON_BOUNCE_TIME)
            gpio.add_event_detect(BUTTON_RIGHT, gpio.FALLING, callback=self.cocktail_navigation_callback, bouncetime=BUTTON_BOUNCE_TIME)
            self.ignore_button_presses=0

    def refresh_cocktail_list(self):
        print("Attempting to retreive cocktail list from REST API...")

        try:
            response=requests.get(self.api_addr+"/cocktails")
            available=1
        except:
            available=0

        if available==0:
            time.sleep(1)
            self.refresh_cocktail_list()
        else:
            if response.status_code!=200:
                self.refresh_cocktail_list()
            else:
                self.cocktails=json.loads(response.text)['cocktails']

    def display_screensaver(self):
        lcd.lcd_init()
        lcd.lcd_string(" Murge Machine ", 0x80)
        lcd.lcd_string("      v0.1     ", 0x8C0)

    def refresh_screen(self):
        lcd.lcd_init()
        lcd.lcd_string(self.cocktails[self.position]['name'], 0x80)
        lcd.lcd_string("<      o       >", 0x8C0)

    def display_cocktail_size_choice(self):
        lcd.lcd_init()
        lcd.lcd_string("     Size?      ", 0x80)
        lcd.lcd_string("25cl   <    50cl", 0x8C0)

if __name__ == "__main__":
    hmi=HMI("http://localhost:2636")
    while(1):
        pass