


"""
Tuning systems are a mess.
    https://en.wikipedia.org/wiki/Musical_tuning#Tuning_systems
    https://en.wikipedia.org/wiki/Concert_pitch
"""

class ET12(): # 12 tone equal temperament
    twelth_root_of_2 = 1.05946309435929526455
    relative_to_c = {
        'c': 0,
        'd': 2,
        'e': 4,
        'f': 5,
        'g': 7,
        'a': 9,
        'b': 11,
    }
    
    def __init__(self, **kwargs):
        if len(kwargs) > 1:
            raise TypeError()
        self.tones = dict()
        self.base_tone, self.base_freq = list(kwargs.items())[0]
        for octave in [2,3,4,5,6]:
            for note in self.relative_to_c:
                self.get('{}{}'.format(note, octave))

    def get(self, tone):
        if tone not in self.tones:
            self.tones[tone] = self.base_freq * self.ratio(tone, self.base_tone)
        return self.tones[tone]
        
    def ratio(self, a, b):
        octaves = int(a[1]) - int(b[1])
        semitones = self.relative_to_c[a[0]] - self.relative_to_c[b[0]]
        exponent = octaves * 12 + semitones
        return self.twelth_root_of_2 ** exponent

