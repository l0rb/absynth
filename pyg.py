#!/usr/bin/python3

import sys
import wave
import pygame
from pygame.locals import *
from io import BytesIO
import numpy as np

from play import make_frames, make_wav, song, sampwidth, framerate

def make_buffer(song, mode='natural'):
    #b = BytesIO()
    #music = wave.open(b, 'wb')
    #music.setnchannels(1)
    #music.setframerate(framerate)
    #music.setcomptype('NONE', 'Not Compressed')
    #music.setsampwidth(sampwidth)
    
    frames = np.array(make_frames(song, mode, 'pygame'), dtype=np.int16)
    #music.writeframes(frames)
    #music.close()
    return frames


resolution = 100,100
framerate = 44100

pygame.mixer.pre_init(frequency=framerate, size=16, channels=1)
pygame.init()
pygame.mixer.init()
pygame.display.set_mode(resolution)

dur = 0.4
notes = {
    'c4': pygame.mixer.Sound(buffer=make_buffer([(261.6, dur)])),
    'e4': pygame.mixer.Sound(buffer=make_buffer([(329.6, dur)])),
    'a4': pygame.mixer.Sound(buffer=make_buffer([(440, dur)])),
    'c5': pygame.mixer.Sound(buffer=make_buffer([(523.3, dur)])),
}
keys = {
    K_a: 'c4',
    K_s: 'e4',
    K_d: 'a4',
    K_f: 'c5',
}

while True:
    for event in pygame.event.get():
        print(event)
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
            sys.exit()
        if (event.type == KEYDOWN and event.key in [K_a, K_s, K_d, K_f]):
            note = notes[keys[event.key]]
            note.play()


