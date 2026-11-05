"""Render the original supplied atlases without altering their pixels or colors."""
import math
import random
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
                        if min(c.r,c.g,c.b)>210:surface.set_at((x,y),(0,0,0,0))
                        elif name=='tree' and min(c.r,c.g,c.b)>125 and max(c.r,c.g,c.b)-min(c.r,c.g,c.b)<45:surface.set_at((x,y),(0,0,0,0))
        for name in ('almond','walnut','acorn'):
            self.sheets[name]=self.sheets[name].subsurface(self.sheets[name].get_bounding_rect()).copy()
        rng=random.Random(71)
        self.stars=[(rng.randrange(1100),rng.randrange(95,280),rng.choice([1,1,1,2])) for _ in range(65)]
        self.cache={}
    def sprite(self,key,rect,width):
        cache=(key,tuple(rect),width)
        if cache not in self.cache:
            s=self.sheets[key].subsurface(rect)
            self.cache[cache]=pg.transform.smoothscale(s,(width,max(1,round(s.get_height()*width/s.get_width()))))
        return self.cache[cache]
    def blit(self,g,key,rect,width,x,bottom):
        s=self.sprite(key,rect,width);g.canvas.blit(s,(round(x),round(bottom-s.get_height())))
    def night_surface(self,s):
        key=('night',id(s))
        if key not in self.cache:
            dark=s.copy();dark.fill((105,145,170,255),special_flags=pg.BLEND_RGBA_MULT)
            self.cache[key]=dark
        return self.cache[key]
    def item(self,g,key,width,x,bottom,flip=False):
        sheet=self.sheets[key];s=self.sprite(key,sheet.get_rect(),width)
        if g.world.night and key not in ('almond','walnut','acorn'):s=self.night_surface(s)
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
        if n:
            for i,(sx,sy,radius) in enumerate(self.stars):
                brightness=int(175+55*math.sin(w.time*.8+i))
                pg.draw.circle(g.canvas,(brightness,brightness,220),(sx,sy),radius)
        pg.draw.circle(g.canvas,(227,235,213) if n else (248,203,111),(880,115),34)
        forest=self.sprite('forest',(0,445 if n else 0,1774,442 if n else 443),1100)
        offset=w.distance*.22%1100
        for x in (-offset,1100-offset):g.canvas.blit(forest,(round(x),529-forest.get_height()))
        pg.draw.rect(g.canvas,(25,37,36) if n else (58,51,31),(0,662,1100,18))
        # Persistent world-space tiles share one rounded boundary. No screen clipping
        # and no terrain overdraw through transparent pit openings.
        for kind,start,width in w.terrain:
            left=round(start-w.distance);right=round(start+width-w.distance)
            if right<0 or left>1100:continue
            self.item(g,kind,right-left,left,666 if kind=='pit' else 662)
        pg.draw.rect(g.canvas,(25,37,36) if n else (58,51,31),(0,666,1100,14))
    def object(self,g,o):
        k,x,y,w,h=o[:5];flip=bool(o[5]) if len(o)>5 else False
        if k=='pit':return  # The terrain stream draws this tile exactly once.
        elif k=='tree':
            self.item(g,'tree',240,x-5,526,flip)
        else:
            width={'rock':round(w*62/52),'bird':65,'almond':40,'walnut':42,'acorn':42}[k]
            if k in ('almond','walnut','acorn'):
                glow=pg.Surface((84,84),pg.SRCALPHA)
                for radius in range(40,8,-2):
                    pg.draw.circle(glow,(255,202,90,int((41-radius)*1.4)),(42,42),radius)
                g.canvas.blit(glow,(round(x+width/2-42),round(y+h-20-42)))
            self.item(g,k,width,x,y+h,flip if k in ('rock','bird') else False)
