import wave
from math import sin, pi
from struct import pack

framerate = 44100
sampwidth = 1 # in bytes, setting to 1 gives us 8 bit music
pack_constant = 'b' # see python documentation, needs to be congruent for sampwidth
max_val = 2 ** (sampwidth * 8 - 1) - 1 # maximum value of a signed int with sampwidth*8 bits
harmonics = 7

def make_wav(song, filename='music.wav'):
    music = wave.open(filename, 'wb')
    music.setnchannels(1)
    music.setframerate(framerate)
    music.setcomptype('NONE', 'Not Compressed')
    music.setsampwidth(sampwidth)
    
    frames = bytes()
    for note in song:
        duration = note[1]
        freqs = [note[0] * i for i in range(1, harmonics+1)]
        periods = [float(framerate)/freq for freq in freqs]
        frame_rads = [2*pi / float(period) for period in periods]
        for frame in range(round(framerate * duration)):
            value = max_val * sum([sin(frame_rad *frame) for frame_rad in frame_rads]) / harmonics
            frame = pack('='+pack_constant, round(value))
            frames += frame
            #music.writeframesraw(frame)

    music.writeframes(frames)
    music.close()


song = [
    (440, 0.4),
    (261, 0.4),
    (440, 0.4),
    (293, 0.4),
    (440, 0.4),
    (329, 0.4),
    (440, 0.4),
    (349, 0.4),
]

make_wav(song, 'harmonic.wav')
