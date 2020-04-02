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
            while 1:
                self.strip.fill(tuple(int((color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4)))
        except:
            pass

    def set_fading_color(self, color):
        pass

    def set_chasing_color_threaded(self, color):
        self.stop_running_light_thread()
        self.light_thread=multiprocessing.Process(target=self.set_chasing_color_blocking, args=(color,))
        self.light_thread.start()

    def set_chasing_color_blocking(self, color):
        try:
            while 1:
                for i in range(1, self.led_count-2):
                    self.strip[i+1]=tuple(int((color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4))
                    time.sleep(CHASE_BUFFER_TIME)
                    self.strip[i-1]=(0,0,0)
        except:
            pass

    def set_strobing_color_threaded(self, color, frequency):
        self.stop_running_light_thread()
        self.light_thread=multiprocessing.Process(target=self.set_strobing_color_blocking, args=(color,frequency,))
        self.light_thread.start()

    def set_strobing_color_blocking(self, color, frequency):
        try:
            while 1:
                self.strip.fill(tuple(int((color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4)))
                time.sleep(0.5/frequency)
                self.strip.fill((0,0,0))
                time.sleep(0.5/frequency)
        except:
            pass

    def set_rainbow_threaded(self):
        pass

    def set_rainbow_blocking(self):
        pass

    def set_idle_light_config(self, light_config):
        self.idle_light_config=light_config
        self.reset_idle_light_config()

    def reset_idle_light_config(self):
        self.stop_running_light_thread()
        if self.idle_light_config['effect']=="fixed":
            self.set_fixed_color_threaded(self.idle_light_config['color'])
        elif self.idle_light_config['effect']=="rainbow":
            self.set_rainbow_color_threaded()
        elif self.idle_light_config['effect']=="fade":
            self.set_fading_color_threaded(self.idle_light_config['color'])
        elif self.idle_light_config['effect']=="strobe":
            self.set_strobing_color_threaded(self.idle_light_config['color'], self.idle_light_config['frequency'])
        elif self.idle_light_config['effect']=="chase":
            self.set_chasing_color_threaded(self.idle_light_config['color'])

    def stop_running_light_thread(self):
        if hasattr(self, 'light_thread'):
            self.light_thread.terminate()
            del self.light_thread