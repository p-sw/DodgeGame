import pygame as pg

from lib.scene import MenuScene

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
        self.screen = pg.display.set_mode((800, 800),)
        pg.display.set_caption("DodgeGame")
        self.clock = pg.time.Clock()
        self.finished = False
        
        self.change_scene("menu", MenuScene)
    
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
    
    def change_scene(self, status, sceneObjClass, inheritGroups={}):
        self.scene = sceneObjClass(self, inheritGroups)
        self.scene_status = status
    
    def quit(self):
        self.finished = True

if __name__ == "__main__":
    Game().start()