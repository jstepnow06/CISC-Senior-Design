from scipy import signal
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import seaborn as sns
import threading
from glob import glob

import librosa
import librosa.display
from playsound3 import playsound
#from pydub import AudioSegment
from itertools import cycle

import pyaudio
import numpy as np
import matplotlib.pyplot as plt
#Listen to audio
p = pyaudio.PyAudio()

sample_rate = 44100
chunk_size = 1024
audio_chunks = []

stream = p.open(
    format=pyaudio.paFloat32,
    channels=1,
    rate=sample_rate,
    input=True,
    frames_per_buffer=chunk_size
)

print("Listening... press Ctrl+C to stop")

try:
    while True:
        data = stream.read(chunk_size, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.float32)
        audio_chunks.append(audio_data.copy())

except KeyboardInterrupt:
    print("\nRecording stopped.")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()

# Combine all recorded chunks into one array
if audio_chunks:
    audio = np.concatenate(audio_chunks)

    # Time axis in seconds
    time = np.arange(len(audio)) / sample_rate

    # Plot waveform
    plt.figure(figsize=(14, 5))
    plt.plot(time, audio, linewidth=0.5)
    plt.title("Recorded Audio Waveform")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.ylim(-1, 1)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("No audio was recorded.")


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

def gradientStuff(audio, gradient, sample_rate):

    #seperate into 1/10 second chunks
    chunks = []
    chunksG = []
    for i in range(0, len(audio) // 4410):
        chunks.append(audio[i * 4410 : (i + 1) * 4410])
        chunksG.append(gradient[i * 4410 : (i + 1) * 4410])
    #check max of ea. chunk
    maxes = []
    for c in chunks:
        maxes.append(max(c))
    #if > 0.5, keep
    kept_time = []
    for i in range(0, len(maxes)):
        if maxes[i] > 0.3:
            kept_time.append(i)
            print(i/10)
    #check for chunks next to eachother, determine whether they are the same note, remove if they are
    for t in range(0, len(kept_time) - 1):
        #print(kept_time[t+1] - kept_time[t])
        if(kept_time[t+1] - kept_time[t] < 2):
            sum = 0.0
            for grad in chunksG[t]:
                sum += grad
            sum /= len(chunksG)
            print(sum)
            if sum < 0:
                print(str(kept_time[t])+" has a hold note")
        #if gradient is falling its a hold

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
    #audio_files = glob('Trans-Siberian Orchestra - God Rest Ye Merry Gentleman (Official Audio).mp3')
    #playsound(audio_files[0])
    #y, sr = librosa.load(audio_files[0])
    #print(f'y: {y[:10]}')
    #print(f'shape y: {y.shape}')
    #print(f'sr: {sr}')
    #first_5_seconds = int(5 * sr)

    #y_first_5 = y[:first_5_seconds]
    #time_axis = np.arange(len(y_first_5)) / sr

    #plt.figure(figsize=(15, 5))
    #plt.plot(time_axis, y_first_5, lw=0.5, color=color_pal[0])

    #plt.title('Raw Audio - First 5 Seconds')
    #plt.xlabel('Time (seconds)')
    #plt.ylabel('Amplitude')
    #plt.xlim(0, 5)

    #plt.tight_layout()
    #plt.show()


    Window = int(0.05 * 44100)
    second = 6.0 #which second of song you want pitch
    time = int(second * 44100)
    bounds = [20, 1000]
    #print(PitchDetect(audio, Window, time, 44100, bounds))

    peaks = []
    derivative = np.gradient(audio)

    gradientStuff(audio, derivative, 44100)

    #calculate rate of change every 1/10 second (maybe use first derriv)
    for i in range(0, len(audio) // 4410):
        segment = audio[i * 4410 : (i + 1) * 4410]
        rms = np.sqrt(np.mean(segment**2))
        #print(derivative[i])
        if rms >= 0.035:
            #print(PitchDetect(audio, Window, i * 4410, 44100, bounds))
            #print(f"Time: {i / 10:.1f} seconds")
            pass
main()