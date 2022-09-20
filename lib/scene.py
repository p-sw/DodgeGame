from typing import Iterable
import pygame as pg

from lib.object import Text, Color, Button, Colors

class Scene:
    def __init__(self):
        self.groups = {}
        
    def add_item(self, name, *sprites:Iterable[pg.sprite.Sprite]):
        self.groups[name].add(sprites)
    
    def create_group(self, name, *sprites:Iterable[pg.sprite.Sprite]):
        self.groups[name] = pg.sprite.Group(sprites)
        return self.groups[name]
    
    def update(self, events):
        for groups in self.groups.values():
            groups.update(events)
    
    def render(self, screen):
        for groups in self.groups.values():
            for item in groups:
                item.render(screen)

class PreGameScene(Scene):
    def __init__(self, gameObject):
        super().__init__()
        self.screen_color = Colors.WHITE.as_iter()
        
        title_font = pg.font.Font('assets/font/BlackHanSans-Regular.ttf', 40)
        button_font = pg.font.Font('assets/font/BlackHanSans-Regular.ttf', 20)
        self.title = Text("부평고 2022 코딩동아리", title_font, Color(0, 0, 0), (400, 100))
        self.create_group("title", self.title)
        
        BUTTON_COLOR = [
            Colors.ORANGE,
            Colors.RED,
            Colors.RED - Color(100, 0, 0)
        ]
        
        def start_event():
            gameObject.scene = GameScene(gameObject)
        
        def quit_event():
            gameObject.finished = True
            
        
        self.start_button = Button(
            (200, 50),
            (400, 300),
            BUTTON_COLOR,
            Text("시작하기", button_font, Colors.WHITE),
            start_event
        )
        self.quit_button = Button(
            (200, 50),
            (400, 600),
            BUTTON_COLOR,
            Text("종료하기", button_font, Colors.WHITE),
            quit_event
        )
        self.create_group("buttons", self.start_button, self.quit_button)

class GameScene(Scene):
    ...