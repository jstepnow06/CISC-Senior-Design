import pygame
import time
import threading

pygame.mixer.init()

largeBeat = pygame.mixer.Sound(r"Pitch Algorithm\11325622-tr909-kick-drum-241402.mp3")
smallBeat = pygame.mixer.Sound(r"Pitch Algorithm\11325622-tr707-snare-drum-241412.mp3")

a = True

def metronom(bpm, TimeSig):
    bps = bpm / 60
    spb = 1 / bps
    c = 0

    while a:
        if c == 0:
            print("LargeBeat")
            largeBeat.play()
        else:
            print("smallBEat")
            smallBeat.play()

        c += 1
        if c == TimeSig:
            c = 0

        time.sleep(spb)

def otherStuff():
    while a:
        print("doing other stuff")
        time.sleep(1)

# Create threads
metronomeThread = threading.Thread(target=metronom, args=(84, 4))
otherThread = threading.Thread(target=otherStuff)

# Start threads
metronomeThread.start()
otherThread.start()