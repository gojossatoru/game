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
        for name in ('almond','walnut','acorn','bird','rock','tree','ground','pit'):
            path=root/(name+('.png' if name in ('ground','pit') else '.PNG'))
            self.sheets[name]=pg.image.load(str(path)).convert_alpha()
            # White-backed cutouts use white as their transparency key at runtime.
            surface=self.sheets[name]
            if name not in ('ground','pit'):
                for x in range(surface.get_width()):
                    for y in range(surface.get_height()):
                        c=surface.get_at((x,y))
                        if min(c.r,c.g,c.b)>235:surface.set_at((x,y),(c.r,c.g,c.b,0))
        self.cache={}
    def sprite(self,key,rect,width):
        cache=(key,tuple(rect),width)
        if cache not in self.cache:
            s=self.sheets[key].subsurface(rect)
            self.cache[cache]=pg.transform.smoothscale(s,(width,max(1,round(s.get_height()*width/s.get_width()))))
        return self.cache[cache]
    def blit(self,g,key,rect,width,x,bottom):
        s=self.sprite(key,rect,width);g.canvas.blit(s,(round(x),round(bottom-s.get_height())))
    def item(self,g,key,width,x,bottom,flip=False):
        sheet=self.sheets[key];s=self.sprite(key,sheet.get_rect(),width)
        if flip:s=pg.transform.flip(s,True,False)
        g.canvas.blit(s,(round(x),round(bottom-s.get_height())))
    def sleeping(self,g):
        self.blit(g,'boar',(1410,583 if g.world.night else 140,290,200),115,492,397)
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
        for i in range(-1,6):
            index=int(w.distance*.35//360)+i
            self.item(g,'tree',190,i*360-(w.distance*.35%360),515,index%3==0)
        offset=w.distance%350
        for i in range(-1,5):self.item(g,'ground',355,i*350-offset,625)
        pg.draw.rect(g.canvas,(58,51,31),(0,625,1100,55))
    def object(self,g,o):
        k,x,y,w,h=o[:5];flip=bool(o[5]) if len(o)>5 else False
        if k=='pit':self.item(g,'pit',180,x-30,650)
        elif k=='branch':
            self.blit(g,'objects',(1045,640,475,240),105,x,y+h)
        else:
            width={'rock':62,'bird':65,'almond':30,'walnut':32,'acorn':32}[k]
            self.item(g,k,width,x,y+h,flip if k in ('rock','bird') else False)
