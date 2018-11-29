import wave
from math import sin, pi
from struct import pack
import numpy as np

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

class Frames():
    """
    we want to be able to mess with the individual partials of a tone or song,
    and we want to be able to add/subtract waves or whole tones/songs together.
    that is what this class exists for. it is probably most elegant if all the
    partials are themselves Frames() objects? (not super-sure about that, give
    thought to cycles vs non-periodic frames, and also envelops)
    """
    
    def _init_max_val(self):
        self._max_val = 2 ** (self.sampwidth * 8 - 1) - 1 # maximum value of a signed int with sampwidth*8 bits
        return self._max_val

    def __init__(self, framerate=44100, sampwidth=2, duration=0.4):
        self.partials = list()
        self._dtype = np.dtype('i{}'.format(sampwidth))
        self.raw = np.array([], dtype=self._dtype)
        self.framerate = framerate 
        self._dur = duration
        self._nframes = round(self.framerate * self._dur)

        self.sampwidth = sampwidth
        self._init_max_val()

    @property
    def duration(self):
        return self._dur

    @duration.setter
    def setduration(self, value):
        assert not self.raw # only allowed to change duration if no partial exists yet i.e. raw is still an empty list
        self._dur = value
        self._nframes = round(self.framerate * self._dur)

    def apply_asr(self, a=0.1, r=0.2):
        nframes = len(self.raw)
        aframes = nframes * a
        rframes = nframes * r
        for i in range(round(aframes)):
            self.raw[i] *= (i/aframes)
        for i in range(round(rframes)):
            self.raw[i*-1] *= (i/rframes)

    def add_partial(self, p): # p is also a Frame object
        """
        assert len(p.raw) == len(self.raw), "can't add samples of different length (yet)"
        assert p.sampwidth == self.sampwidth, "can't add samples of different width (yet)"
        self.partials.append(p)
        for frame_n, frame_val in enumerate(p.raw):
            self.raw[frame_n] += frame_val
            self.raw[frame_n] /= 2
        """
        pass

    def add_array(self, arr:np.array): # arr has to be numpy array
        assert self._dtype == arr.dtype, "can't add array of different width (yet)"
        if not self.raw:
            self.raw = np.resize(arr, self._nframes)
        else:
            assert len(self.raw) == len(arr)
            self.raw = (self.raw + arr) / 2

    def create_sin_array(self, freq, amp=1, phase=0): # phase is in radians
        assert 0 < amp <= 1
        cycle_length = round(float(self.framerate)/freq) # number of frames in one cycle
        frame_rad = 2*pi / float(cycle_length) # how many radians we progress in one frame
        one_cycle = np.zeros(cycle_length, dtype=self._dtype)
        for frame in range(cycle_length):
            value = sin(phase + frame_rad * frame) * amp * self._max_val
            one_cycle[frame] = round(value)
        full_length = np.resize(one_cycle, self._nframes)
        return full_length

def make_frames2(note, mode='natural', audio_format='wav'):
    frames = list()
    duration = note[1]
    freq = note[0]
    frames = Frames(duration=duration)
    s = frames.create_sin_array(freq)
    frames.add_array(s)
    frames.apply_asr()
    return frames.raw


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
