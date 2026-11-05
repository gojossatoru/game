"""Small, locally synthesized two-part pig grunts; no network or audio assets needed."""
from array import array
import math
import random
import pygame as pg

class Sounds:
    def __init__(self):
        self.normal=self.happy=None
        if not pg.mixer.get_init():return
        rate,fmt,channels=pg.mixer.get_init()
        if fmt!=-16:return
        def grunt(happy):
            rng=random.Random(19);duration=.52 if happy else .32;data=array('h')
            for i in range(int(rate*duration)):
                t=i/rate;part=t/(duration/2)%1
                freq=(185 if happy else 115)*(1+.25*math.sin(part*math.pi*2))
                phase=2*math.pi*freq*t
                value=(math.sin(phase)+.45*math.sin(phase*2)+.2*rng.uniform(-1,1))*math.sin(math.pi*part)**2*.22
                data.extend([int(value*32767)]*channels)
            return pg.mixer.Sound(buffer=data)
        self.normal=grunt(False);self.happy=grunt(True)
    def collect(self,kind):
        sound=self.happy if kind=='acorn' else self.normal
        if sound:sound.play()
