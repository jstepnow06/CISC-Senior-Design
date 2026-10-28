import pygame
import time

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
            chanel = largeBeat.play()
        else:
            print("smallBEat")
            chanel = smallBeat.play()
        c += 1
        if c == TimeSig:
            c = 0
        time.sleep(spb)

metronom(211, 3)