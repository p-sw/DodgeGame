import pygame as pg
from secrets import token_hex

from lib.scene import StudentIDInputScene

class EventWrapper:
    def __init__(self, events):
        self.events = events
    
    def __contains__(self, item):
        return item in self['type']

    def __getitem__(self, key):
        return [event.__getattribute__(key) for event in self.events]

class Game:
    def __init__(self):
        pg.init()
        self.time = pg.time.get_ticks()
        self.screen = pg.display.set_mode((800, 800))
        pg.display.set_caption("DodgeGame")
        self.clock = pg.time.Clock()
        self.finished = False
        self.offline = True
        self.session = str(token_hex(20))
        self.api_url = "http://localhost:5000"
        self.api_authkey = "29ef4415905a63f012beb73ceed61b9a187fad0b"
        
        self.student_grade = None
        self.student_class = None
        self.student_number = None
        
        self.change_scene(StudentIDInputScene)

        self.playable_count = 3

    def start(self):
        while not self.finished:
            self.time = pg.time.get_ticks()
            events = EventWrapper(pg.event.get())
            
            if pg.QUIT in events:
                break
            
            self.screen.fill(self.scene.screen_color)
            self.scene.update(events)
            self.scene.render(self.screen)
            
            pg.display.flip()
        pg.quit()
    
    def change_scene(self, sceneObjClass, datas={}):
        self.scene = sceneObjClass(self, datas)
    
    def quit(self):
        self.finished = True

if __name__ == "__main__":
    Game().start()