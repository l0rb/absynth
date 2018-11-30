
class SineWave():
    def __init__(self, freq, amp, phase):
        self.frequency = freq
        self.amplitude = amp
        self.phase = phase


class Natural():
    def __init__(self, freq, n = 5):
        self.fundamental = freq
        self.partials = list()
        for i in range(1, n+1):
            freq = self.fundamental*i
            amp = 1/i
            self.partials.append(SineWave(freq, amp, phase=0))

    def __iter__(self):
        return self.partials.__iter__()
