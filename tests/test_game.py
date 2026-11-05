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
            w=World();w.objects=[['branch',195,GROUND-78,95,28]];w.step(.001,False,sliding);self.assertEqual(w.over,not sliding)
    def test_pits_and_rocks(self):
        for kind,y,width,height in [('pit',GROUND,120,35),('rock',GROUND-43,52,43)]:
            w=World();w.objects=[[kind,190,y,width,height]];w.step(.001);self.assertTrue(w.over)
            w=World();w.y=GROUND-140;w.objects=[[kind,190,y,width,height]];w.step(.001);self.assertFalse(w.over)
    def test_render(self):
        g=Game()
        for mode in ('title','play','pause','over'):
            g.mode=mode;g.draw()
        g.world.time=45;g.draw()
if __name__=='__main__':unittest.main()
