import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
import unittest
from game import World,Game,GROUND
class Mechanics(unittest.TestCase):
    def test_timing(self):
        w=World();w.time=45;self.assertTrue(w.night);w.time=90;self.assertFalse(w.night)
        w.time=60;self.assertEqual(w.speed,348)
    def test_hold_jump(self):
        heights=[]
        for held in (False,True):
            w=World();w.jump();top=GROUND
            for _ in range(110):w.step(.01,held);top=min(top,w.y)
            heights.append(top)
        self.assertLess(heights[1],heights[0]-40)
    def test_nuts(self):
        w=World()
        for kind,value in [('almond',1),('walnut',5),('acorn',10)]:
            w.objects=[[kind,205,GROUND-40,24,28]];before=w.score;w.step(.001);self.assertEqual(w.score-before,value)
    def test_slide(self):
        for sliding in (False,True):
            w=World();w.objects=[['tree',195,GROUND-78,95,28]];w.step(.001,False,sliding);self.assertEqual(w.over,not sliding)
    def test_pits_and_rocks(self):
        for kind,y,width,height in [('pit',GROUND,120,35),('rock',GROUND-43,52,43)]:
            w=World();w.objects=[[kind,190,y,width,height]];w.step(.001);self.assertTrue(w.over)
            w=World();w.y=GROUND-140;w.objects=[[kind,190,y,width,height]];w.step(.001);self.assertFalse(w.over)
    def test_collection_events(self):
        w=World();w.objects=[['acorn',205,GROUND-40,24,28]]
        w.step(.001);self.assertEqual(w.collected,['acorn'])
        w.step(.001);self.assertEqual(w.collected,[])
    def test_spawn_variation(self):
        heights=set();mirrors=set()
        w=World(7)
        for _ in range(200):
            w.objects=[];w.next=0;w.step(.001)
            for o in w.objects:
                if o[0]=='bird':heights.add(o[2]);mirrors.add(o[5])
        self.assertEqual(len(heights),4);self.assertEqual(mirrors,{False,True})
    def test_night_and_pit_opening(self):
        import pygame as pg
        g=Game();g.activate();g.world.objects=[['pit',790,GROUND,120,35]]
        g.draw()
        # Nothing from the ground tile may appear through the pit opening.
        self.assertEqual(g.canvas.get_at((850,500))[:3],(235,227,193))
        original=pg.Surface((2,2),pg.SRCALPHA);original.fill((200,200,200,255))
        night=g.art.night_surface(original)
        self.assertLess(night.get_at((0,0)).r,original.get_at((0,0)).r)
        self.assertEqual(night.get_at((0,0)).a,255)
        self.assertIsNotNone(g.audio.sad)
        self.assertGreater(g.audio.sad.get_length(),g.audio.normal.get_length())
    def test_render(self):
        g=Game()
        for mode in ('title','play','pause','over'):
            g.mode=mode;g.draw()
        for night in (False,True):
            g.world.time=45 if night else 0
            for mode in ('play','over'):
                g.mode=mode
                for slide in (False,True):
                    g.world.slide=slide
                    for kind in ('almond','walnut','acorn','rock','tree','bird','pit'):
                        g.world.objects=[[kind,600,450,40,30]];g.draw()
            g.world.y=400;g.draw()
if __name__=='__main__':unittest.main()
