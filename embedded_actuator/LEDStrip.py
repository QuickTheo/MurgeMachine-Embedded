import neopixel
import board
import time
import multiprocessing
import ctypes

CHASE_BUFFER_TIME   = 0.06

class CustomLEDStrip():
    def __init__(self, led_count):
        self.strip=neopixel.NeoPixel(board.D18, led_count)
        self.led_count=led_count
        self.idle_light_config=None
        self.strip=neopixel.NeoPixel(board.D18, self.led_count)

    def set_fixed_color_threaded(self, color):
        self.stop_running_light_thread()
        self.light_thread=multiprocessing.Process(target=self.set_fixed_color_blocking, args=(color,))
        self.light_thread.start()

    def set_fixed_color_blocking(self, color):
        try:
            print("Setting fixed color to "+color)
            while 1:
                self.strip.fill(tuple(int((color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4)))
        except:
            print("Thread finishing")

    def set_fading_color(self, color, t):
        pass

    def set_chasing_color(self, hex_color, t):
        t=0
        while t<=float(t):
            for i in range(1, self.led_count-2):
                self.strip[i+1]=tuple(int((hex_color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4))
                time.sleep(CHASE_BUFFER_TIME)
                t+=CHASE_BUFFER_TIME
                self.strip[i-1]=(0,0,0)
        self.reset_idle_light_config()

    def set_strobing_color(self, color, t):
        pass

    def set_rainbow(self, t):
        pass

    def set_idle_light_config(self, light_config):
        self.idle_light_config=light_config
        self.reset_idle_light_config()

    def reset_idle_light_config(self):
        self.stop_running_light_thread()
        self.set_fixed_color_threaded("#00ff00")

    def stop_running_light_thread(self):
        if hasattr(self, 'light_thread'):
            self.light_thread.terminate()
            del self.light_thread