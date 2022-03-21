#!/usr/bin/python3
import pygame
import time
import gpiozero as gpio
import _thread as thread
from array import array
from pygame.locals import *
from morse_lookup import *

pygame.mixer.pre_init(44100, -16, 1, 1024)
pygame.init()

class ToneSound(pygame.mixer.Sound):
    def __init__(self, frequency, volume):
        self.frequency = frequency
        pygame.mixer.Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        period = int(round(pygame.mixer.get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

def decoder_thread():
    global key_up_time
    global buffer
    new_word = False
    while True:
        time.sleep(.01)
        key_up_length = time.time() - key_up_time
        if len(buffer) > 0 and key_up_length >= 5*unit:
            new_word = True
            bit_string = "".join(buffer)
            try_decode(bit_string)
            del buffer[:]
        elif new_word and key_up_length >= 15*unit:
            new_word = False
            sys.stdout.write(" ")
            sys.stdout.flush()

tone = 650
tone_obj = ToneSound(frequency = tone, volume = .5)

dit_pin = 23
dit = gpio.Button(dit_pin, pull_up=True)
dah_pin = 24
dah = gpio.Button(dah_pin, pull_up=True)

wpm = 18
unit = 60/(50*wpm)

DOT = "."
DASH = "-"

key_down_time = 0
key_down_length = 0
key_up_time = 0
buffer = []

thread.start_new_thread(decoder_thread, ())

print("Ready")

while True:
    if dit.is_pressed:
      key_down_time = time.time()
      tone_obj.play(-1)
      time.sleep(unit)
      key_up_time = time.time()
      tone_obj.stop()
      time.sleep(unit)
      key_down_length = key_up_time - key_down_time
      buffer.append(DOT)
      
    if dah.is_pressed:
      key_down_time = time.time()
      tone_obj.play(-1)
      time.sleep(unit*3)
      key_up_time = time.time()
      tone_obj.stop()
      time.sleep(unit)
      key_down_length = key_up_time - key_down_time
      buffer.append(DASH)
