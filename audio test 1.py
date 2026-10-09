from scipy import signal
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import seaborn as sns

from glob import glob

import librosa
import librosa.display
from playsound3 import playsound
#from pydub import AudioSegment
from itertools import cycle

sns.set_theme(style="white", palette=None)
color_pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]
color_cycle = cycle(plt.rcParams["axes.prop_cycle"].by_key()["color"])

def practiceFunc(x):
    f_0 = 1
    return np.sin(x * np.pi * 2 * f_0)

def ACF_Function(f, Window, time, lag):
    return np.sum(f[time : time + Window] * f[lag + time: lag + Window + time])
def DF_Function(f, Window, time, lag):
    return ACF_Function(f, Window, time, 0) \
    + ACF_Function(f, Window, time + lag, 0) \
    - 2 * ACF_Function(f, Window, time, lag)
def normalize(f, Window, time, lag):
    if lag == 0:
        return 1
    return DF_Function(f, Window, time, lag) / np.sum([DF_Function(f, Window, time, j + 1) for j in range(lag)]) * lag


def PitchDetect(f, Window, time, sampleRate, bounds):
    DF_VALUES = [normalize(f, Window, time, i) for i in range(*bounds)]
    sample = np.argmin(DF_VALUES) + bounds[0]
    return sampleRate / sample

def main():
    print("hi")
    sample_rate = 500
    start = 0
    end = 5
    num_samples = int(sample_rate * (end - start) + 1)
    Window = 200
    bounds = [20, num_samples // 2]
    x = np.linspace(start, end, num_samples)
    print(PitchDetect(practiceFunc(x), Window, 1, sample_rate, bounds))
    audio_files = glob('Trans-Siberian Orchestra - God Rest Ye Merry Gentleman (Official Audio).mp3')
    #playsound(audio_files[0])
    y, sr = librosa.load(audio_files[0])
    print(f'y: {y[:10]}')
    print(f'shape y: {y.shape}')
    print(f'sr: {sr}')
    first_5_seconds = int(5 * sr)

    y_first_5 = y[:first_5_seconds]
    time_axis = np.arange(len(y_first_5)) / sr

    plt.figure(figsize=(15, 5))
    plt.plot(time_axis, y_first_5, lw=0.5, color=color_pal[0])

    plt.title('Raw Audio - First 5 Seconds')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    plt.xlim(0, 5)

    plt.tight_layout()
    plt.show()


    Window = int(0.05 * sr)
    second = 6.0 #which second of song you want pitch
    time = int(second * sr)
    bounds = [20, 1000]
    print(PitchDetect(y, Window, time, sr, bounds))


main()