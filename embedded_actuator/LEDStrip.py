import neopixel
import board
import time
import multiprocessing
import ctypes

CHASE_BUFFER_TIME   = 0.05
FADE_BUFFER_TIME    = 0.01
RAINBOW_BUFFER_TIME = 0.01

class CustomLEDStrip(neopixel.NeoPixel):
    def __init__(self, led_count):
        super(CustomLEDStrip, self).__init__(board.D18, led_count, auto_write=False)
        self.led_count=led_count
        self.idle_light_config=None

    def set_fixed_color_threaded(self, color):
        self.stop_running_light_thread()
        self.light_thread=multiprocessing.Process(target=self.set_fixed_color_blocking, args=(color,))
        self.light_thread.start()

    def set_fixed_color_blocking(self, color):
        while 1:
            self.fill(tuple(int((color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4)))
            self.show()

    def set_fading_color_threaded(self, color):
        self.stop_running_light_thread()
        self.light_thread=multiprocessing.Process(target=self.set_fading_color_blocking, args=(color,))
        self.light_thread.start()

    def set_fading_color_blocking(self, color):
        while 1:
            for i in range(1,100):
                self.brightness=(i/100)
                self.fill(tuple(int((color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4)))
                self.show()
                time.sleep(FADE_BUFFER_TIME)
            for i in range(100,1,-1):
                self.brightness=(i/100)
                self.fill(tuple(int((color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4)))
                self.show()
                time.sleep(FADE_BUFFER_TIME)

    def set_chasing_color_threaded(self, color):
        self.stop_running_light_thread()
        self.light_thread=multiprocessing.Process(target=self.set_chasing_color_blocking, args=(color,))
        self.light_thread.start()

    def set_chasing_color_blocking(self, color):
        while 1:
            for i in range(0, self.led_count):
                self[i]=tuple(int((color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4))
                self.show()
                time.sleep(CHASE_BUFFER_TIME)
                if(i-1)>=0:
                    self[i-1]=(0,0,0)
                else:
                    self[self.led_count-1]=(0,0,0)
                self.show()

    def set_strobing_color_threaded(self, color, frequency):
        self.stop_running_light_thread()
        self.light_thread=multiprocessing.Process(target=self.set_strobing_color_blocking, args=(color,frequency,))
        self.light_thread.start()

    def set_strobing_color_blocking(self, color, frequency):
        while 1:
            self.fill(tuple(int((color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4)))
            self.show()
            time.sleep(0.5/frequency)
            self.fill((0,0,0))
            self.show()
            time.sleep(0.5/frequency)

    def set_rainbow_threaded(self):
        self.stop_running_light_thread()
        self.light_thread=multiprocessing.Process(target=self.set_rainbow_blocking)
        self.light_thread.start()

    def set_rainbow_blocking(self):
        while 1:
            for j in range(255):
                for i in range(self.led_count):
                    pixel_index = (i * 256 // self.led_count) + j
                    self[i] = self.wheel(pixel_index & 255)
                self.show()
                time.sleep(RAINBOW_BUFFER_TIME)

    def set_idle_light_config(self, light_config):
        self.idle_light_config=light_config
        self.reset_idle_light_config()

    def reset_idle_light_config(self):
        self.stop_running_light_thread()
        if self.idle_light_config['effect']=="fixed":
            self.set_fixed_color_threaded(self.idle_light_config['color'])
        elif self.idle_light_config['effect']=="rainbow":
            self.set_rainbow_threaded()
        elif self.idle_light_config['effect']=="fade":
            self.set_fading_color_threaded(self.idle_light_config['color'])
        elif self.idle_light_config['effect']=="strobe":
            self.set_strobing_color_threaded(self.idle_light_config['color'], 20)
        elif self.idle_light_config['effect']=="chase":
            self.set_chasing_color_threaded(self.idle_light_config['color'])

    def stop_running_light_thread(self):
        if hasattr(self, 'light_thread'):
            self.light_thread.terminate()
            del self.light_thread

    def wheel(self, pos):
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b)