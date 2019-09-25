from machine import Pin, Neopixel
import time
# from helpers import _wheel

import conf
import conf_tree


class AnimationController():

    def __init__(self, led_type):
        self.led_type = led_type
        self.animation = 'blank'
        self.conf = conf
        self.params = {}
        self.len = self.conf.ring_len if led_type == 'ring' else self.conf.strip_len
        self.rise_start_ms = [False, False]
        self.rise_color = [False, False]
        self.rise_duration_ms = [1000, 1000]
        self.rise_dir = [False, False]
        self.rotation_dir = False
        self.rotation_color = False
        self.show_idle = False
        self.show_rainbow = False
        self.rising_status = [False, False]
        self.offset = 0

        self.leds = Neopixel(Pin(self.conf.pins[led_type]), self.len)
        # self.leds.timings(((700,600), (350, 800), 60000))
        print(self.leds)

    def process(self):
        self.now_ms = time.ticks_ms()

        # # reducing blinking
        # if self.animation is 'rise' and self.rise_animation_finished():
        #     return
        animation = getattr(self, self.animation)
        animation()
        self.leds.show()

    def animate(self, animation, params=False):
        print(self.led_type, "will animate", animation)
        self.params = params
        self.animation = animation

        if animation is 'blank':
            self.leds.clear()
            self.leds.show()

        if animation is 'rise':
            odd_even = params[0]
            direction = params[1]
            color = params[2] if direction == 'start' else Neopixel.BLACK

            self.rise_start_ms[odd_even] = time.ticks_ms()

            if odd_even == 0 and direction == 'start' or odd_even == 1 and direction == 'rewind':
                self.rise_dir[odd_even] = "up"
            else:
                self.rise_dir[odd_even] = "down"
            self.rise_color[odd_even] = color
            self.rise_duration_ms[odd_even] = self.conf.animation_rise_duration_ms if direction == 'start' else self.conf.animation_rewind_duration_ms
            self.rising_status[odd_even] = True
        if animation is 'rotate':
            self.rotation_dir = params[0]
            self.rotation_color = params[1]

    def rise_animation_finished(self):
        if self.rising_status[0] or self.rising_status[1]:
            return False
        return True

    def _wave(self, offset):
        if offset > 0.5:
            offset = 1 - offset
        return offset * 2 

    def _lerp_colors(self, c1, c2, t):
        c1 = self.leds.RGBtoHSB(c1)
        c2 = self.leds.RGBtoHSB(c2)
        # print(c1)
        # print(c2)

        hue = self._lerp(c1[0], c2[0], t)
        sat = self._lerp(c1[1], c2[1], t)
        val = self._lerp(c1[2], c2[2], t)
        # print(hue, sat, val)
        return self.leds.HSBtoRGB(hue, sat, val)

    def _lerp(self, a,  b,  f):
        return a + f * (b - a)

    def fill(self, color):
        for i in range(self.len):
            self.leds.set(i, color, 0, 1, False)

    ## animations ##

    def blank(self):
        pass

    def breath(self):
        period_ms = self.conf.animation_breath_period_ms
        offset = (self.now_ms % period_ms)/period_ms
        color = self.leds.RGBtoHSB(Neopixel.CYAN)
        
        val = color[2] * self._wave(offset)
        color = self.leds.HSBtoRGB(color[0], color[1], val)
        self.fill(color)

    def offline(self):
        period_ms = self.conf.animation_breath_period_ms
        offset = (self.now_ms % period_ms)/period_ms
        color = self._wave(Neopixel.RED, Neopixel.MAGENTA, offset)
        self.fill(color)

    def rainbow(self):
        sat = 1.0
        bri = 0.2
        period_ms = conf.animation_rainbow_period_ms
        offset = (self.now_ms % period_ms)/period_ms
        for i in range(self.len):
            dHue = 360.0/self.len*(offset * self.len + i)
            hue = dHue % 360
            self.leds.setHSB(i + 1, hue, sat, bri, 1, False)

    def rise(self):

        for odd_even in range(2):

            if not self.rising_status[odd_even]:
                continue

            end_time_ms = self.rise_start_ms[odd_even] + \
                self.rise_duration_ms[odd_even]

            period_ms = self.rise_duration_ms[odd_even] // self.len
            active_px = (
                self.now_ms - self.rise_start_ms[odd_even]) // period_ms

            # check animation time is over
            if active_px > self.len:
                self.rising_status[odd_even] = False
                continue
            for i in range(self.len):
                if i > active_px:
                    continue
                j = i
                if self.rise_dir[odd_even] == "down":
                    j = self.len - j - 1
                if j % 2 == odd_even:
                    self.leds.set(j, self.rise_color[odd_even], 0, 1, False)

    def rotate(self):
        width_px = self.len // 2
        color_bg = Neopixel.WHITE
        period_ms = self.conf.animation_rotation_period_ms // self.len
        active_px = (self.now_ms // period_ms) % self.len

        last_px_offset = (self.now_ms % period_ms) / period_ms
        first_px_offset = 1 - last_px_offset

        color = {}
        for i in range(self.len):
            if i == 0:
                color[i] = self._lerp_colors(
                    color_bg, self.rotation_color, first_px_offset)
            elif i == width_px:
                color[i] = self._lerp_colors(
                    color_bg, self.rotation_color, last_px_offset)
            elif i > 0 and i < width_px:
                color[i] = self.rotation_color
            else:
                color[i] = color_bg

        # now shift result forward for active_px
        for i in range(self.len):
            j = (i + active_px) % self.len
            if self.rotation_dir == "ccw":
                j = self.len - j - 1
            self.leds.set(j, color[i], 0, 1, False)


def rgb_int2tuple(rgbint):
    return (rgbint // 256 // 256 % 256, rgbint // 256 % 256, rgbint % 256)


def int2tuple_rgb(rgb_tuple):
    print("rgb_tuple", rgb_tuple)
    rgb_int = rgb_tuple[0] << 16 | rgb_tuple[1] << 8 | rgb_tuple[2]
    return rgb_int
