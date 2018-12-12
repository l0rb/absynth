import numpy as np
import math

float_t = np.dtype('f8')

def sin(cycle_length, amp=1, phase=0): # phase is in radians
    assert 0 < amp <= 1
    #cycle_length = round(float(self.framerate)/freq) # number of frames in one cycle
    frame_rad = 2*math.pi / float(cycle_length) # how many radians we progress in one frame
    one_cycle = np.zeros(cycle_length, dtype=float_t)
    for frame in range(cycle_length):
        one_cycle[frame] = math.sin(phase + frame_rad * frame)
    one_cycle *= amp
    return one_cycle

def sawtooth(cycle_length, amp=1, phase=0, upwards=True): # phase in [0, 1]
    assert 0 < amp <= 1
    assert 0 <= phase <= 1
    one_cycle = np.zeros(cycle_length, dtype=float_t)
    if upwards:
        it = range(cycle_length)
    else:
        it = range(cycle_length-1, -1, -1)
    for frame in it:
        one_cycle[frame] = 2 * (float(frame)/cycle_length) - 1
    one_cycle = np.roll(one_cycle, round(phase*cycle_length))
    one_cycle *= amp
    return one_cycle
