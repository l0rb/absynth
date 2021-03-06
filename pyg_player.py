#!/usr/bin/python3

import sys
import wave
import pygame
from pygame.locals import *
import tuning
from time import sleep

from play import make_frames, make_sndarray, make_wav, song, sampwidth, framerate

pygame.mixer.pre_init(frequency=framerate, size=sampwidth*8, channels=1)
pygame.init()
pygame.mixer.init()

#tuned = tuning.ET12(a4=466) # chorton pitch
#tuned = tuning.ET12(a4=415) # modern baroque
#tuned = tuning.ET12(a4=440) # iso16
tuned = tuning.ET12(c4=256) # verdi tuning

def compose(song, dur=0.5):
    composition = list()
    for note in song:
        if isinstance(note, str):
            tone = (tuned.get(note), dur)
        else:
            tone = (tuned.get(note[0]), dur*note[1])
        composition.append(tone)
    return composition

ninth = ['b3', 'b3', 'c4', 'd4', 'd4', 'c4', 'b3', 'a3', 'g3', 'g3', 'a3', 'b3', ('b3', 1.5), ('a3', 0.5), ('a3', 2),
         'b3', 'b3', 'c4', 'd4', 'd4', 'c4', 'b3', 'a3', 'g3', 'g3', 'a3', 'b3', ('a3', 1.5), ('g3', 0.5), ('g3', 2)]

composition = compose(ninth, 0.3)

snd_array = make_sndarray(composition, mode='dense')
song = pygame.sndarray.make_sound(snd_array)
print('play')
c = song.play()
while c.get_busy():
    sleep(0.2)

