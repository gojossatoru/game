"""Little Boar — an offline, native forest runner."""
import json, math, os, random
from pathlib import Path
import pygame as pg

W,H,GROUND=1100,680,510
JUMP={pg.K_SPACE,pg.K_UP,pg.K_w}
SAVE=Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local/share'))/'LittleBoar'/'score.json'

def read_best():
    try: return max(0,int(json.loads(SAVE.read_text())['best']))
    except (OSError,ValueError,KeyError,TypeError): return 0

class World:
    def __init__(self,seed=None):
        self.rng=random.Random(seed); self.time=0.; self.distance=0.; self.y=GROUND; self.vy=0.; self.slide=False
        self.score=0; self.over=False; self.objects=[]; self.next=2.; self.nut_timer=.65; self.hold=0.
    @property
    def speed(self): return 330+min(180,18*int(self.time//60))
    @property
    def night(self): return int(self.time//45)%2==1
    @property
    def player(self): return pg.Rect(187,self.y-(29 if self.slide else 57),69,27 if self.slide else 53)
    def jump(self):
        if self.y==GROUND and not self.over: self.vy=-540; self.hold=0; self.slide=False
    def step(self,dt,held=False,slide=False):
        if self.over:return
        self.time+=dt; self.distance+=self.speed*dt
        self.slide=slide and self.y==GROUND
        gravity=620 if held and self.vy<0 and self.hold<.28 else 1700
        self.hold+=dt; self.vy+=gravity*dt; self.y=min(GROUND,self.y+self.vy*dt)
        if self.y==GROUND:self.vy=0
        self.next-=dt; self.nut_timer-=dt
        if self.next<=0:
            kind=self.rng.choice(['rock','branch','bird','pit'])
            size={'rock':(52,43),'branch':(95,28),'bird':(58,30),'pit':(120,35)}[kind]
            y=GROUND-size[1] if kind=='rock' else GROUND-78 if kind in ('bird','branch') else GROUND
            self.objects.append([kind,float(W+60),y,*size]); self.next=self.rng.uniform(1.8,2.6)
        if self.nut_timer<=0:
            kind=self.rng.choices(['almond','walnut','acorn'],[80,17,3])[0]
            self.objects.append([kind,float(W+60),GROUND-self.rng.choice([55,120,175]),24,28]);self.nut_timer=self.rng.uniform(.65,1.15)
        for obj in self.objects[:]:
            kind,x,y,w,h=obj; obj[1]-=self.speed*dt
            rect=pg.Rect(obj[1],y,w,h)
            if kind in ('almond','walnut','acorn'):
                if self.player.colliderect(rect):self.score+={'almond':1,'walnut':5,'acorn':10}[kind];self.objects.remove(obj)
            elif kind=='pit':
                if rect.left+10<self.player.centerx<rect.right-10 and self.y>=GROUND-4:self.over=True
            elif self.player.colliderect(rect):self.over=True
            if obj in self.objects and obj[1]<-150:self.objects.remove(obj)

class Game:
    def __init__(self):
        pg.init();pg.display.set_caption('Little Boar • Forest Run');self.screen=pg.display.set_mode((W,H),pg.RESIZABLE)
        self.canvas=pg.Surface((W,H));self.clock=pg.time.Clock();self.fonts={s:pg.font.SysFont('dejavusans',s,bold=True) for s in (14,18,24,36,68)}
        self.world=World();self.mode='title';self.best=read_best();self.saved=False;self.running=True;self.keys=set()
    def text(self,s,x,y,size=18,color=(246,237,207),center=False):
        image=self.fonts[size].render(str(s),True,color);self.canvas.blit(image,image.get_rect(center=(x,y)) if center else (x,y))
    def ellipse(self,c,r):pg.draw.ellipse(self.canvas,c,r)
    def boar(self):
        w=self.world;x=177;y=w.y; low=w.slide; bob=math.sin(w.time*20)*3 if y==GROUND and self.mode=='play' else 0
        y+=bob; height=32 if low else 55
        for i in range(4):
            dx=math.sin(w.time*19+i*2)*9 if self.mode=='play' else 0
            pg.draw.line(self.canvas,(86,53,42),(x+18+i*15,y-16),(x+15+i*15+dx,y-2),10)
        self.ellipse((151,95,61),(x,y-height-6,82,height));self.ellipse((170,109,70),(x+53,y-height-7,40,height-1))
        for i in range(3):pg.draw.arc(self.canvas,(244,209,146),(x+9,y-height+2+i*11,49,15),.2,2.8,5)
        pg.draw.polygon(self.canvas,(124,75,52),[(x+60,y-height+3),(x+59,y-height-23),(x+76,y-height-3)])
        self.ellipse((233,157,136),(x+78,y-30 if not low else y-23,25,21));pg.draw.circle(self.canvas,(32,29,23),(x+78,int(y-height+16)),4)
        for dx in (85,94):pg.draw.line(self.canvas,(105,65,54),(x+dx,y-23 if not low else y-16),(x+dx-1,y-17 if not low else y-10),3)
        pg.draw.arc(self.canvas,(130,82,54),(x-15,y-38,23,20),2,5.7,4)
    def scenery(self):
        w=self.world;n=w.night;sky=(23,42,58) if n else (230,221,181);self.canvas.fill(sky)
        if n:
            for i in range(45):pg.draw.circle(self.canvas,(183,202,190),((i*137)%W,45+(i*73)%245),1)
        pg.draw.circle(self.canvas,(224,231,202) if n else (246,191,90),(880,125),40)
        for layer in range(3):
            color=([(42,69,76),(35,82,80),(29,65,61)] if n else [(166,181,128),(113,145,100),(66,111,77)])[layer]
            offset=w.distance*(.12+layer*.13)%180
            for i in range(-1,9):
                x=i*180-offset;top=220+layer*65+math.sin(i*7)*30
                pg.draw.rect(self.canvas,color,(x+65,top+55,20,GROUND-top))
                for yy,rr in [(top+60,65),(top+30,50),(top,32)]:pg.draw.circle(self.canvas,color,(int(x+75),int(yy)),rr)
        pg.draw.rect(self.canvas,(47,51,39) if n else (110,86,55),(0,GROUND,W,H-GROUND))
        pg.draw.rect(self.canvas,(59,104,79) if n else (137,164,77),(0,GROUND,W,10))
        for i in range(65):
            x=(i*83-w.distance)%W;y=GROUND+28+(i*29)%140
            self.ellipse((67,64,45) if n else (131,103,65),(x,y,9,4))
    def object(self,o):
        k,x,y,w,h=o;x=int(x)
        if k=='pit':
            pg.draw.rect(self.canvas,(17,27,29),(x,y,w,110));pg.draw.line(self.canvas,(66,52,38),(x,y+110),(x+w,y+110),6)
        elif k=='rock':
            pg.draw.polygon(self.canvas,(114,122,126),[(x,y+h),(x+8,y+13),(x+29,y),(x+45,y+17),(x+w,y+h)])
            pg.draw.polygon(self.canvas,(160,167,162),[(x+8,y+13),(x+29,y),(x+35,y+12),(x+14,y+29)])
        elif k=='branch':
            pg.draw.line(self.canvas,(91,69,46),(x,y+22),(x+w,y+12),13)
            for i in range(4):self.ellipse((102,142,79),(x+12+i*20,y-5,23,15))
        elif k=='bird':
            self.ellipse((161,108,75),(x,y+7,48,23));self.ellipse((234,210,168),(x+8,y+18,32,13))
            flap=math.sin(self.world.time*15)*13
            pg.draw.polygon(self.canvas,(133,83,57),[(x+20,y+15),(x+45,y-15+flap),(x+42,y+20)])
            pg.draw.polygon(self.canvas,(223,176,89),[(x,y+13),(x-10,y+18),(x+3,y+20)]);pg.draw.circle(self.canvas,(26,30,25),(x+9,y+12),3)
        else:
            if k=='acorn':pg.draw.circle(self.canvas,(206,166,70),(x+12,y+14),22,1)
            self.ellipse((213,150,77) if k!='walnut' else (177,115,64),(x,y,w,h))
            if k=='acorn':
                self.ellipse((111,75,43),(x-2,y-2,28,12));pg.draw.line(self.canvas,(108,78,47),(x+12,y),(x+15,y-8),4)
            else:
                for i in range(2):pg.draw.arc(self.canvas,(246,195,120),(x+4+i*6,y+3,10,22),1,4.8,2)
    def button(self,label):
        r=pg.Rect(405,400,290,62);pg.draw.rect(self.canvas,(225,178,88),r,border_radius=18);self.text(label,550,431,24,(48,61,44),True);return r
    def draw(self):
        self.scenery()
        for o in self.world.objects:self.object(o)
        self.boar();pg.draw.rect(self.canvas,(38,62,48),(20,15,240,72),border_radius=14);pg.draw.rect(self.canvas,(38,62,48),(W-195,15,175,76),border_radius=14);self.text('LITTLE BOAR',34,25,24);self.text('FOREST RUN',35,57,14,(167,186,143))
        self.text(f'{self.world.score:04d}',W-175,22,36);self.text(f'BEST {self.best:04d}',W-174,67,14)
        self.text(('NIGHT' if self.world.night else 'DAY')+f'  •  {int(self.world.time)//60:02}:{int(self.world.time)%60:02}',470,30,18,(128,153,121))
        self.text('↑ / W / SPACE  jump • hold for longer     ↓ / S  slide     P / ESC  pause',550,641,14,center=True)
        if self.mode!='play':
            shade=pg.Surface((W,H),pg.SRCALPHA);shade.fill((10,25,24,190));self.canvas.blit(shade,(0,0))
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
                if self.world.over:
                    self.mode='over';self.best=max(self.best,self.world.score)
                    try:
                        SAVE.parent.mkdir(parents=True,exist_ok=True);temp=SAVE.with_suffix('.tmp');temp.write_text(json.dumps({'best':self.best}));temp.replace(SAVE)
                    except OSError:pass
            self.draw()
        pg.quit()

if __name__=='__main__':Game().run()
