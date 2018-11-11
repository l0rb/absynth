import wave
from math import sin, pi
from struct import pack

framerate = 44100
sampwidth = 4 # in bytes, setting to 1 gives us 8 bit music
max_val = 2 ** (sampwidth * 8 - 1) - 1 # maximum value of a signed int with sampwidth*8 bits
harmonics = 7

def pack_correct(val):
    # see python documentation, number of bits needs to be congruent for sampwidth
    pack_constant = {
        1: 'b',
        2: 'h',
        4: 'i',
        8: 'q',
    }[sampwidth]
    return pack('=' + pack_constant, round(val))

def make_frequencies(fundamental):
    #return [fundamental * i for i in range(1, harmonics+1)] # natural progression
    return [fundamental * (i*2+1) for i in range(harmonics)]

def make_amplitudes(mode = 'natural'):
    if mode == 'stringed':
        return [1./((i*2+1)**2) for i in range(harmonics)]
    if mode == 'natural':
        return [1./i for i in range(1, harmonics+1)]
    if mode == 'equal':
        return [1 for i in range(1, harmonics+1)]
    if mode == 'geometric':
        return [1./(2**i) for i in range(1, harmonics+1)]

def make_wav(song, filename='music.wav', mode='natural'):
    music = wave.open(filename, 'wb')
    music.setnchannels(1)
    music.setframerate(framerate)
    music.setcomptype('NONE', 'Not Compressed')
    music.setsampwidth(sampwidth)
    
    frames = bytes()
    for note in song:
        duration = note[1]
        freqs = make_frequencies(note[0])
        periods = [float(framerate)/freq for freq in freqs]
        frame_rads = [2*pi / float(period) for period in periods]
        amps = make_amplitudes(mode)
        max_val = float(globals()['max_val']) / sum(amps)
        for frame in range(round(framerate * duration)):
            value = max_val * sum([sin(rad_amp[0] *frame)*rad_amp[1] for rad_amp in zip(frame_rads, amps)])
            frame = pack_correct(value)
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

make_wav(song, 'try_guitar.wav', 'stringed')
