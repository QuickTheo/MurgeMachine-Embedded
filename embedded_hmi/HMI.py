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

connect_attempts=0

class HMI:
    def __init__(self, api_addr, buttons):
        self.api_addr=api_addr
        self.button_bounce_time=300
        self.buttons=buttons

        lcd.lcd_init()

        gpio.setmode(gpio.BCM)
        for button in self.buttons:
            gpio.setup(button, gpio.IN)
            gpio.add_event_detect(button, gpio.FALLING, callback=self.cocktail_navigation_callback, bouncetime=self.button_bounce_time)

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
            if button==self.buttons[0]:
                print("Next cocktail")
                if self.position==0:
                    self.position=len(self.cocktails)-1
                else:
                    self.position-=1
                self.refresh_screen()
            elif button==self.buttons[1]:
                print("'"+self.cocktails[self.position]['name']+"' selected")
                for button in self.buttons:
                    gpio.remove_event_detect(button)
                    gpio.add_event_detect(button, gpio.FALLING, callback=self.cocktail_size_select_callback, bouncetime=self.button_bounce_time)
                self.display_cocktail_size_choice()
            elif button==self.buttons[2]:
                print("Previous cocktail")
                if self.position==len(self.cocktails)-1:
                    self.position=0
                else:
                    self.position+=1
                self.refresh_screen()
            self.ignore_button_presses=0

    def cocktail_size_select_callback(self, button):
        if self.ignore_button_presses==0:
            self.ignore_button_presses=1
            headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
            if button==self.buttons[1]:
                print("Back")
            else:
                try:
                    size=(25 if button==self.buttons[0] else 50)
                    print("Requesting preparation of "+str(size)+" of "+self.cocktails[self.position]['name']+"...")
                    data={'cocktailId':self.cocktails[self.position]['id'],'size':size,'light':{'color':'','effect':''}}
                    r=requests.post(self.api_addr+"/request-cocktail", data=json.dumps(data), headers=headers)
                    if r.status_code==200:
                        print("Cocktail requested")
                    else:
                        print("Cocktail request error")
                        self.display_drink_not_found()
                        for button in self.buttons:
                            gpio.remove_event_detect(button)
                            gpio.add_event_detect(button, gpio.FALLING, callback=self.cocktail_navigation_callback, bouncetime=self.button_bounce_time)
                        while not(gpio.event_detected(self.buttons[0])) and not(gpio.event_detected(self.buttons[1])) and not(gpio.event_detected(self.buttons[2])):
                            pass
                except:
                    self.refresh_cocktail_list()
            self.refresh_screen()
            for button in self.buttons:
                gpio.remove_event_detect(button)
                gpio.add_event_detect(button, gpio.FALLING, callback=self.cocktail_navigation_callback, bouncetime=self.button_bounce_time)
            self.ignore_button_presses=0

    def refresh_cocktail_list(self):
        global connect_attempts

        if connect_attempts==0:
            print("Attempting to connect to REST API", end = '', flush=True)
            lcd.lcd_string(" Connecting to ", 0x80)
            lcd.lcd_string("   REST API", 0x8C0) 

        if connect_attempts<3:
            connect_attempts+=1
            lcd.lcd_string(" Connecting to ", 0x80)
            lcd.lcd_string("   REST API"+connect_attempts*".", 0x8C0)
            print(".", end = '', flush=True)
        else:
            connect_attempts=0
            print("")

        try:
            response=requests.get(self.api_addr+"/available-cocktails")
            available=1
        except:
            available=0

        if available==0:
            time.sleep(0.5)
            self.refresh_cocktail_list()
        else:
            if response.status_code!=200:
                time.sleep(0.5)
                self.refresh_cocktail_list()
            else:
                print("\nConnected")
                self.cocktails=json.loads(response.text)['cocktails']

    def display_screensaver(self):
        lcd.lcd_init()
        lcd.lcd_string(" Murge Machine ", 0x80)
        lcd.lcd_string("      v0.1     ", 0x8C0)
        
    def display_drink_not_found(self):
        lcd.lcd_init()
        lcd.lcd_string("   404 ERROR    ", 0x80)
        lcd.lcd_string("DRINK NOT FOUND ", 0x8C0)

    def refresh_screen(self):
        lcd.lcd_init()
        lcd.lcd_string(self.cocktails[self.position]['name'], 0x80)
        lcd.lcd_string("<      o       >", 0x8C0)

    def display_cocktail_size_choice(self):
        lcd.lcd_init()
        lcd.lcd_string("     Size?      ", 0x80)
        lcd.lcd_string("25cl   <    50cl", 0x8C0)

if __name__ == "__main__":
    hmi=HMI("http://localhost:2636", buttons=[17, 27, 22])
    while(1):
        pass