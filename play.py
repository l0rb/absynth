import wave
from math import sin, pi
from struct import pack

framerate = 44100
sampwidth = 2 # in bytes, setting to 1 gives us 8 bit music
max_val = 2 ** (sampwidth * 8 - 1) - 1 # maximum value of a signed int with sampwidth*8 bits
harmonics = 7

def pack_correct(val, audio_format='wav'):
    if audio_format == 'wav':
        # see python documentation, number of bits needs to be congruent for sampwidth
        pack_constant = {
            1: 'b',
            2: 'h',
            4: 'i',
            8: 'q',
        }[sampwidth]
        return pack('=' + pack_constant, round(val))
    if audio_format in ['int', 'pygame']:
        return int(round(val))

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

def make_phases(mode = 'equal'):
    if mode in ['equal', 'natural']:
        return [1 for i in range(1, harmonics+1)]
    if mode == 'stringed':
        return [pi*((i-1)%2) for i in range(1, harmonics+1)]

def adsr(frame, nframes, a=0.1, d=0.05, s=0.55, r=0.1, minimum=0.02, sustain_at=0.400):
    assert (a+d+s+r - 1) < 0.0001 # so we can assume them summing to 1 from here on
    relative_position = float(frame) / nframes
    if relative_position < a:
        return max(relative_position / a, minimum)
    relative_position -= a
    if relative_position < d:
        return 1 - (relative_position / d) * (1-sustain_at)
    relative_position -= d
    if relative_position < s:
        return sustain_at
    relative_position -= s
    return max(1 - relative_position / r, minimum)

def make_wav(song, filename='music.wav', mode='natural'):
    f = open(filename, 'wb')
    music = wave.open(f)
    music.setnchannels(1)
    music.setframerate(framerate)
    music.setcomptype('NONE', 'Not Compressed')
    music.setsampwidth(sampwidth)
    
    frames = make_frames(song, mode)
    
    music.writeframes(frames)
    music.close()
    return f

def make_frames(song, mode='natural', audio_format='wav'):
    frames = list()
    for note in song:
        duration = note[1]
        freqs = make_frequencies(note[0])
        periods = [float(framerate)/freq for freq in freqs]
        frame_rads = [2*pi / float(period) for period in periods]
        amps = make_amplitudes(mode)
        phases = make_phases(mode)
        max_val = float(globals()['max_val']) / sum(amps)
        nframes = round(framerate * duration)
        for frame in range(nframes):
            # TODO: make this more performant by doing only 1 cycle
            value = max_val * sum([sin(phase + rads * frame) * amp for rads, amp, phase in zip(frame_rads, amps, phases)])
            value *= adsr(frame, nframes)
            frame = pack_correct(value, audio_format)
            frames.append(frame)
    if audio_format == 'wav':
        frames = b''.join(frames)
    return frames


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

#make_wav(song, 'try_guitar_envelope.wav', 'stringed')
