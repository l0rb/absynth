import wave
from math import sin, pi
from struct import pack

framerate = 44100
sampwidth = 1 # in bytes, setting to 1 gives us 8 bit music
pack_constant = 'b' # see python documentation, needs to be congruent for sampwidth

freq = 440
duration = 5 # in seconds
max_val = 2 ** (sampwidth * 8 - 1) - 1 # maximum value of a signed int with sampwidth*8 bits

music = wave.open('music.wav', 'wb')
music.setnchannels(1)
music.setframerate(framerate)
music.setcomptype('NONE', 'Not Compressed')
music.setsampwidth(sampwidth)


song = [
    (440, 0.5),
    (261, 0.5),
    (440, 0.5),
    (293, 0.5),
    (440, 0.5),
    (329, 0.5),
    (440, 0.5),
    (349, 0.5),
]
frames = bytes()
for note in song:
    freq = note[0]
    duration = note[1]
    period = float(framerate)/freq
    frame_rad = 2*pi / float(period)
    for frame in range(round(framerate * duration)):
        value = max_val * sin( frame_rad * frame )
        frame = pack('='+pack_constant, round(value))
        frames += frame
        #music.writeframesraw(frame)

music.writeframes(frames)
music.close()
