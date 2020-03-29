import I2C_LCD_driver
import RPi.GPIO as gpio
import time

#Button configuration
BUTTON_LEFT         = 17
BUTTON_OK           = 27
BUTTON_RIGHT        = 22
BUTTON_BOUNCE_TIME  = 300

#Button callbacks
def button_pressed(channel):
    print(str(channel)+" pressed")

#lcd=I2C_LCD_driver.lcd()
#lcd.lcd_display_string("MURGE MACHINE",1)
gpio.setmode(gpio.BCM)
gpio.setup(BUTTON_LEFT, gpio.IN)
gpio.setup(BUTTON_OK, gpio.IN)
gpio.setup(BUTTON_RIGHT, gpio.IN)
gpio.add_event_detect(BUTTON_LEFT, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)
gpio.add_event_detect(BUTTON_OK, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)
gpio.add_event_detect(BUTTON_RIGHT, gpio.FALLING, callback=button_pressed, bouncetime=BUTTON_BOUNCE_TIME)

while(1):
    pass