"""Render the original supplied atlases without altering their pixels or colors."""
import math
from pathlib import Path
import pygame as pg

class Art:
    def __init__(self):
        root=Path(__file__).resolve().parent/'sprites'
        self.sheets={key:pg.image.load(str(root/name)).convert_alpha() for key,name in {
            'forest':'Day and night forest atlas.png',
            'boar':'Eight boars sprite atlas.png',
            'terrain':'Woodland terrain atlas_ daylight and moonlight.png',
            'objects':'Transparent six-object sprite atlas.png'}.items()}
        self.cache={}
    def sprite(self,key,rect,width):
        cache=(key,tuple(rect),width)
        if cache not in self.cache:
            s=self.sheets[key].subsurface(rect)
            self.cache[cache]=pg.transform.smoothscale(s,(width,max(1,round(s.get_height()*width/s.get_width()))))
        return self.cache[cache]
    def blit(self,g,key,rect,width,x,bottom):
        s=self.sprite(key,rect,width);g.canvas.blit(s,(round(x),round(bottom-s.get_height())))
    def boar(self,g):
        w=g.world
        pose=3 if g.mode=='over' else 2 if w.slide else 1 if w.y<510 else 0
        # Each pose retains its original proportions; only its display size changes.
        regions=[(65,118,340,225),(510,110,320,220),(950,145,340,200),(1410,140,290,200)]
        x,y,sw,sh=regions[pose];y+=443 if w.night else 0
        bob=math.sin(w.time*18)*2 if pose==0 and g.mode=='play' else 0
        self.blit(g,'boar',(x,y,sw,sh),108,170,w.y+4+bob)
    def scenery(self,g):
        w=g.world;n=w.night
        g.canvas.fill((21,40,55) if n else (235,227,193))
        pg.draw.circle(g.canvas,(227,235,213) if n else (248,203,111),(880,115),34)
        forest=self.sprite('forest',(0,443 if n else 0,1774,444 if n else 443),1400)
        offset=w.distance*.22%1400
        for x in (-offset,1400-offset):g.canvas.blit(forest,(x,510-forest.get_height()))
        # Repeat the exact ground tile; pit artwork is drawn over the path.
        offset=w.distance%240
        for i in range(-1,6):self.blit(g,'terrain',(1280,443 if n else 0,494,443),250,i*240-offset,580)
        pg.draw.rect(g.canvas,(33,47,43) if n else (92,75,49),(0,580,1100,100))
    def object(self,g,o):
        k,x,y,w,h=o;n=g.world.night
        if k=='rock':self.blit(g,'terrain',(470,443 if n else 0,370,443),82,x-15,517)
        elif k=='pit':self.blit(g,'terrain',(855,443 if n else 0,410,443),400,x-145,695)
        else:
            regions={'almond':(95,150,315,220),'walnut':(610,125,320,270),'acorn':(1150,90,290,330),
                     'bird':(570,610,400,280),'branch':(1045,640,475,240)}
            width={'almond':26,'walnut':30,'acorn':30,'bird':65,'branch':105}[k]
            self.blit(g,'objects',regions[k],width,x,y+h)
