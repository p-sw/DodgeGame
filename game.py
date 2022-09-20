import pygame as pg

from lib.scene import PreGameScene

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        pg.display.set_caption("DodgeGame")
        self.clock = pg.time.Clock()
        self.finished = False
        
        self.pre = PreGameScene(self)
        self.game = None
    
    def start(self):
        while not self.finished:
            self.clock.tick(60)
            events = pg.event.get()
            if pg.QUIT in events:
                break
            
            if not self.game:
                self.screen.fill(self.pre.screen_color)
                self.pre.update(events)
                self.pre.render(self.screen)
            else:
                self.screen.fill(self.game.screen_color)
                self.game.update(events)
                self.game.render(self.screen)
            
            pg.display.flip()
            
        
        pg.quit()
