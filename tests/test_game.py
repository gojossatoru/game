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
            w=World();w.objects=[['tree',195,GROUND-88,95,40]];w.step(.001,False,sliding);self.assertEqual(w.over,not sliding)
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
        # Persistent terrain tiles must join exactly in world coordinates.
        for a,b in zip(g.world.terrain,g.world.terrain[1:]):self.assertEqual(a[1]+a[2],b[1])
        original=pg.Surface((2,2),pg.SRCALPHA);original.fill((200,200,200,255))
        night=g.art.night_surface(original)
        self.assertLess(night.get_at((0,0)).r,original.get_at((0,0)).r)
        self.assertEqual(night.get_at((0,0)).a,255)
        self.assertIsNotNone(g.audio.sad)
        self.assertGreater(g.audio.sad.get_length(),g.audio.normal.get_length())
    def test_terrain_stream_and_rock_sizes(self):
        w=World(17);sizes=set();seen_pit=False
        for _ in range(1600):
            w.over=False;w.y=GROUND-250;w.vy=0;w.next=0
            w.step(.02)
            for a,b in zip(w.terrain,w.terrain[1:]):
                self.assertEqual(a[1]+a[2],b[1])
                self.assertEqual(round(a[1]+a[2]-w.distance),round(b[1]-w.distance))
            seen_pit |= any(t[0]=='pit' for t in w.terrain)
            sizes.update(o[3] for o in w.objects if o[0]=='rock')
            w.objects=[]
        self.assertTrue(seen_pit);self.assertEqual(sizes,{104,156})
    def test_smooth_theme_and_spacing(self):
        w=World()
        for time,expected in [(44.99,0),(45,0),(47,.5),(49,1),(90,1),(92,.5),(94,0)]:
            w.time=time;self.assertAlmostEqual(w.night_mix,expected)
        w.objects=[['rock',500,424,104,86]]
        self.assertFalse(w.clear_for_obstacle(800,100))
        self.assertTrue(w.clear_for_obstacle(1300,100))
    def test_big_rock_jump_clearance(self):
        w=World();w.jump();top=GROUND
        for _ in range(100):w.step(.01,True);top=min(top,w.y)
        self.assertLess(top,GROUND-150)
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
