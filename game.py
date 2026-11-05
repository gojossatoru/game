"""Little Boar — an offline, native forest runner."""
import json, math, os, random
from pathlib import Path
import pygame as pg
from art import Art
from sound import Sounds

W,H,GROUND=1100,680,510
JUMP={pg.K_SPACE,pg.K_UP,pg.K_w}
SAVE=Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local/share'))/'LittleBoar'/'score.json'

def read_best():
    try: return max(0,int(json.loads(SAVE.read_text())['best']))
    except (OSError,ValueError,KeyError,TypeError): return 0

class World:
    def __init__(self,seed=None):
        self.rng=random.Random(seed); self.time=0.; self.distance=0.; self.y=GROUND; self.vy=0.; self.slide=False
        self.terrain=[('ground',i*490,490) for i in range(4)]; self.terrain_end=1960
        self.collected=[]; self.score=0; self.over=False; self.objects=[]; self.next=2.; self.nut_timer=.65; self.hold=0.
    @property
    def speed(self): return 330+min(180,18*int(self.time//60))
    @property
    def night(self): return int(self.time//45)%2==1
    @property
    def player(self): return pg.Rect(187,self.y-(29 if self.slide else 57),69,27 if self.slide else 53)
    def jump(self):
        if self.y==GROUND and not self.over: self.vy=-540; self.hold=0; self.slide=False
    def step(self,dt,held=False,slide=False):
        self.collected.clear()
        if self.over:return
        self.time+=dt; self.distance+=self.speed*dt
        self.slide=slide and self.y==GROUND
        gravity=620 if held and self.vy<0 and self.hold<.28 else 1700
        self.hold+=dt; self.vy+=gravity*dt; self.y=min(GROUND,self.y+self.vy*dt)
        if self.y==GROUND:self.vy=0
        while self.terrain_end < self.distance+W+700:
            kind='pit' if self.terrain[-1][0]!='pit' and self.rng.random()<.22 else 'ground'
            width=200 if kind=='pit' else 490
            if kind=='pit':self.objects.append(['pit',self.terrain_end-self.distance+40+self.speed*dt,GROUND,120,35])
            self.terrain.append((kind,self.terrain_end,width));self.terrain_end+=width
        self.terrain=[tile for tile in self.terrain if tile[1]+tile[2]>=self.distance-10]
        self.next-=dt; self.nut_timer-=dt
        if self.next<=0:
            kind=self.rng.choice(['rock','tree','bird'])
            size={'rock':(52,43),'tree':(220,28),'bird':(58,30),'pit':(120,35)}[kind]
            if kind=='rock' and self.rng.random()<.4:size=(78,65)
            y=GROUND-size[1] if kind=='rock' else GROUND-78 if kind in ('bird','tree') else GROUND
            if kind=='bird':y=GROUND-self.rng.choice([65,100,145,190])
            if not any(t=='pit' and start < self.distance+W+60+size[0] and start+width > self.distance+W+60 for t,start,width in self.terrain):
                self.objects.append([kind,float(W+60),y,*size,self.rng.random()<.5])
            self.next=self.rng.uniform(1.8,2.6)
        if self.nut_timer<=0:
            kind=self.rng.choices(['almond','walnut','acorn'],[80,17,3])[0]
            self.objects.append([kind,float(W+60),GROUND-self.rng.choice([55,120,175]),34,36]);self.nut_timer=self.rng.uniform(.65,1.15)
        for obj in self.objects[:]:
            kind,x,y,w,h=obj[:5]; obj[1]-=self.speed*dt
            rect=pg.Rect(obj[1],y,w,h)
            if kind in ('almond','walnut','acorn'):
                if self.player.colliderect(rect):self.collected.append(kind);self.score+={'almond':1,'walnut':5,'acorn':10}[kind];self.objects.remove(obj)
            elif kind=='pit':
                if rect.left+10<self.player.centerx<rect.right-10 and self.y>=GROUND-4:self.over=True
            elif self.player.colliderect(rect):self.over=True
            if obj in self.objects and obj[1]<-150:self.objects.remove(obj)

class Game:
    def __init__(self):
        pg.init();pg.display.set_caption('Little Boar • Forest Run');self.screen=pg.display.set_mode((W,H),pg.RESIZABLE)
        self.canvas=pg.Surface((W,H));self.clock=pg.time.Clock();self.fonts={s:pg.font.SysFont('dejavusans',s,bold=True) for s in (14,18,24,36,68)}
        self.audio=Sounds();self.art=Art();self.world=World();self.mode='title';self.best=read_best();self.saved=False;self.running=True;self.keys=set()
    def text(self,s,x,y,size=18,color=(246,237,207),center=False):
        image=self.fonts[size].render(str(s),True,color);self.canvas.blit(image,image.get_rect(center=(x,y)) if center else (x,y))
    def ellipse(self,c,r):pg.draw.ellipse(self.canvas,c,r)
    def boar(self):self.art.boar(self)
    def scenery(self):self.art.scenery(self)
    def object(self,o):self.art.object(self,o)
    def button(self,label):
        r=pg.Rect(405,400,290,62);pg.draw.rect(self.canvas,(225,178,88),r,border_radius=18);self.text(label,550,431,24,(48,61,44),True);return r
    def draw(self):
        self.scenery()
        for o in self.world.objects:self.object(o)
        if self.mode!='over':self.boar()
        pg.draw.rect(self.canvas,(38,62,48),(20,15,240,72),border_radius=14);pg.draw.rect(self.canvas,(38,62,48),(W-195,15,175,76),border_radius=14);self.text('LITTLE BOAR',34,25,24);self.text('FOREST RUN',35,57,14,(167,186,143))
        self.text(f'{self.world.score:04d}',W-175,22,36);self.text(f'BEST {self.best:04d}',W-174,67,14)
        self.text(('NIGHT' if self.world.night else 'DAY')+f'  •  {int(self.world.time)//60:02}:{int(self.world.time)%60:02}',470,30,18,(128,153,121))
        self.text('↑ / W / SPACE  jump • hold for longer     ↓ / S  slide     P / ESC  pause',550,641,14,center=True)
        if self.mode!='play':
            shade=pg.Surface((W,H),pg.SRCALPHA);shade.fill((10,25,24,190));self.canvas.blit(shade,(0,0))
            if self.mode=='over':self.art.sleeping(self)
            self.text('A LITTLE BOAR. A BIG ADVENTURE.',550,174,14,(203,180,119),True)
            title={'title':'Into the woods','over':'Game over','pause':'Take a breather'}[self.mode]
            self.text(title,550,245,68,center=True)
            self.text(f'Score  {self.world.score}     •     Best  {self.best}' if self.mode=='over' else 'Leap over rocks and pits. Duck beneath branches and birds.',550,322,18,center=True)
            self.button({'title':'Let’s run','over':'Play again','pause':'Resume'}[self.mode])
            self.text('ALMOND +1  ·  common     WALNUT +5  ·  rare     ACORN +10  ·  legendary',550,507,14,center=True)
            self.text('Press Enter to begin' if self.mode=='title' else 'Press Enter to continue',550,550,14,(161,179,158),True)
        size=self.screen.get_size();scale=min(size[0]/W,size[1]/H);self.offset=((size[0]-W*scale)/2,(size[1]-H*scale)/2);self.scale=scale
        self.screen.fill((13,24,23));self.screen.blit(pg.transform.smoothscale(self.canvas,(int(W*scale),int(H*scale))),self.offset);pg.display.flip()
    def activate(self):
        if self.mode in ('title','over'):self.world=World();self.saved=False
        self.mode='play';self.keys.clear()
    def run(self):
        while self.running:
            dt=min(self.clock.tick(120)/1000,.04)
            for e in pg.event.get():
                if e.type==pg.QUIT:self.running=False
                elif e.type==pg.WINDOWFOCUSLOST:
                    self.keys.clear()
                    if self.mode=='play':self.mode='pause'
                elif e.type==pg.KEYDOWN:
                    self.keys.add(e.key)
                    if e.key in (pg.K_ESCAPE,pg.K_p):self.mode='pause' if self.mode=='play' else 'play' if self.mode=='pause' else self.mode
                    elif e.key==pg.K_RETURN and self.mode!='play':self.activate()
                    elif e.key in JUMP and self.mode=='play':self.world.jump()
                elif e.type==pg.KEYUP:self.keys.discard(e.key)
                elif e.type==pg.MOUSEBUTTONDOWN and e.button==1 and self.mode!='play':
                    pos=((e.pos[0]-self.offset[0])/self.scale,(e.pos[1]-self.offset[1])/self.scale)
                    if pg.Rect(405,400,290,62).collidepoint(pos):self.activate()
            if self.mode=='play':
                self.world.step(dt,bool(self.keys&JUMP),bool(self.keys&{pg.K_DOWN,pg.K_s}))
                for kind in self.world.collected:self.audio.collect(kind)
                if self.world.over:
                    self.audio.game_over();self.mode='over';self.best=max(self.best,self.world.score)
                    try:
                        SAVE.parent.mkdir(parents=True,exist_ok=True);temp=SAVE.with_suffix('.tmp');temp.write_text(json.dumps({'best':self.best}));temp.replace(SAVE)
                    except OSError:pass
            self.draw()
        pg.quit()

if __name__=='__main__':Game().run()
