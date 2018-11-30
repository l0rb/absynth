
class SineWave():
    def __init__(self, freq, amp, phase):
        self.frequency = freq
        self.amplitude = amp
        self.phase = phase

class IterPartials():
    def __iter__(self):
        return self.partials.__iter__()

class Dense(IterPartials):
    def __init__(self, freq, density=10):
        self.fundamental = freq
        self.partials = list()
        self.partials.append(SineWave(freq, amp=1, phase=0))
        for i in range(1, density):
            freq = self.fundamental*(i/density)
            amp = 0.8
            self.partials.append(SineWave(freq, amp, phase=0))
        #self.partials.append(SineWave(freq, amp, phase=0))

twelth_root_of_2 = 1.05946309435929526455
class Tempered(IterPartials):
    def __init__(self, freq, n=5, factor=twelth_root_of_2):
        self.fundamental = freq
        self.partials = list()
        for i in range(0, n):
            freq = self.fundamental * (factor ** i)
            amp = 1/(i+2)
            self.partials.append(SineWave(freq, amp, phase=0))

class Natural(IterPartials):
    def __init__(self, freq, n=5):
        self.fundamental = freq
        self.partials = list()
        for i in range(1, n+1):
            freq = self.fundamental*i
            amp = 1/i
            self.partials.append(SineWave(freq, amp, phase=0))
