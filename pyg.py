#!/usr/bin/python3

import sys
import wave
import pygame
from pygame.locals import *
import tuning

from play import make_frames, make_sndarray, make_wav, song, sampwidth, framerate

#framerate = 44100

pygame.mixer.pre_init(frequency=framerate, size=sampwidth*8, channels=1)
pygame.init()
pygame.mixer.init()

resolution = 100,100
pygame.display.set_mode(resolution)


#tuned = tuning.ET12(a4=466) # chorton pitch
#tuned = tuning.ET12(a4=415) # modern baroque
#tuned = tuning.ET12(a4=440) # iso16
tuned = tuning.ET12(c4=256) # verdi tuning

tones = dict()
keys = dict()
def add_tone(tone, key, dur=0.4):
    f = tuned.get(tone)
    snd_array = make_sndarray([(f, dur)])
    tones[tone] = pygame.sndarray.make_sound(snd_array)
    keys[key] = tone

add_tone('c4', K_a)
add_tone('e4', K_s)
add_tone('a4', K_d)
add_tone('c5', K_f)

while True:
    for event in pygame.event.get():
        print(event)
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
            sys.exit()
        if (event.type == KEYDOWN and event.key in keys):
            tone = tones[keys[event.key]]
            tone.play()


