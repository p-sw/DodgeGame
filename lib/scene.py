from typing import Iterable
from random import randint
from math import log
import pygame as pg

from lib.object import Text, Color, Button, Colors, ButtonEvent
from lib.object import Player, Enemy

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
    
    def inherit_groups(self, *group_names):
        return {name: self.groups[name] for name in group_names}

class MenuScene(Scene):
    def __init__(self, gameObject, inheritGroups):
        super().__init__()
        self.screen_color = Colors.WHITE.as_iter()
        
        title_font = pg.font.Font('assets/font/BlackHanSans-Regular.ttf', 40)
        button_font = pg.font.Font('assets/font/BlackHanSans-Regular.ttf', 20)
        title = Text("부평고 2022 코딩동아리", title_font, Color(0, 0, 0), (400, 100))
        self.create_group("title", title)
        
        BUTTON_COLOR = [
            Colors.ORANGE,
            Colors.RED,
            Colors.RED - Color(100, 0, 0)
        ]
        
        start_button = Button(
            (200, 50),
            (400, 400),
            BUTTON_COLOR,
            Text("시작하기", button_font, Colors.WHITE),
            ButtonEvent(gameObject, lambda gameObject: gameObject.change_scene("game", GameScene))
        )
        quit_button = Button(
            (200, 50),
            (400, 500),
            BUTTON_COLOR,
            Text("종료하기", button_font, Colors.WHITE),
            ButtonEvent(gameObject, lambda gameObject: gameObject.quit())
        )
        self.create_group("buttons", start_button, quit_button)

class GameScene(Scene):
    def __init__(self, gameObject, inheritGroups):
        self.game = gameObject
        super().__init__()
        self.started_time = pg.time.get_ticks()
        self.screen_color = Colors.WHITE.as_iter()
        
        self.player = Player((gameObject.screen.get_width() // 2, gameObject.screen.get_height() // 2), Colors.BLUE)
        self.create_group("player", self.player)
        
        self.score = 0
        self.summon_count = 0
        self.last_summon_time = 0
        self.lower_limit = 100
        
        self.target_x_range = 50  # * 2
        self.target_y_range = 50  # * 2
        
        self.create_group("enemy")
    
    def update(self, events):
        elapsed_time = pg.time.get_ticks() - self.started_time
        
        def hit_test(item, offset):
            return self.player.mask.overlap(item.mask, offset)
        
        def normal_hit(item):
            self.player.set_test_hitbox("normal_hitbox")
            return hit_test(item, (self.player.rect.x - item.rect.x,
                             self.player.rect.y - item.rect.y))
        
        def point_hit(item):
            self.player.set_test_hitbox("point_hitbox")
            return hit_test(item, (((self.player.rect.x - (self.player.point_hitbox_expand_x / 2)) -item.rect.x),
                                   ((self.player.rect.y - (self.player.point_hitbox_expand_y / 2)) - item.rect.y)))
        
        for item in self.groups["enemy"].sprites():
            self.player.set_test_hitbox("normal_hitbox")
            if normal_hit(item):
                self.player.kill()
                self.game.change_scene("result", ResultScene, self.inherit_groups("enemy"))
            elif point_hit(item) and not item.counted:
                item.counted = True
                self.score += 1
        
        # if pg.sprite.groupcollide(self.groups["player"], self.groups["enemy"], True, False):
        #    self.game.change_scene("result", ResultScene, self.inherit_groups("enemy"))
        
        enemy_summon_delay_pattern = lambda x: -0.000005 * (x ** 2) + 500
        summon_delay = enemy_summon_delay_pattern(elapsed_time)
        if summon_delay <= self.lower_limit:
            summon_delay = self.lower_limit
        print(f"elapsed: {elapsed_time}, summon: {self.last_summon_time+summon_delay}, delay: {summon_delay}", end="\r")
        
        if elapsed_time > self.last_summon_time + summon_delay:
            self.add_item("enemy", Enemy(
                randint(-5, 5),
                randint(-5, 5),
                (
                    randint(self.player.rect.x - self.target_x_range, self.player.rect.x + self.target_x_range),
                    randint(self.player.rect.y - self.target_y_range, self.player.rect.y + self.target_y_range)
                ),
                True if randint(0, 1) == 1 else False,
                True if randint(0, 1) == 1 else False,
                self.game.screen.get_size(),
                Colors.RED
            ))
            self.last_summon_time = elapsed_time
        
        super().update(events)

class ResultScene(Scene):
    def __init__(self, gameObject, inheritGroups):
        self.scene_start_time = pg.time.get_ticks()
        self.screen_color = Colors.WHITE.as_iter()
        self.groups = inheritGroups
        
        title = Text("Game Over", pg.font.Font('assets/font/BlackHanSans-Regular.ttf', 40), Colors.BLACK, (400, 100))
        self.create_group("title", title)
        
        BUTTON_COLOR = [
            Colors.CYAN,
            Colors.BLUE,
            Colors.BLUE - Color(0, 0, 100)
        ]
        
        RestartBtn = Button(
            (200, 50),
            (400, 400),
            BUTTON_COLOR,
            Text("다시하기", pg.font.Font('assets/font/BlackHanSans-Regular.ttf', 20), Colors.WHITE),
            ButtonEvent(gameObject, lambda gameObject: gameObject.change_scene("game", GameScene))
        )
        
        MenuBtn = Button(
            (200, 50),
            (400, 500),
            BUTTON_COLOR,
            Text("메뉴로", pg.font.Font('assets/font/BlackHanSans-Regular.ttf', 20), Colors.WHITE),
            ButtonEvent(gameObject, lambda gameObject: gameObject.change_scene("menu", MenuScene))
        )
        
        QuitBtn = Button(
            (200, 50),
            (400, 600),
            BUTTON_COLOR,
            Text("종료하기", pg.font.Font('assets/font/BlackHanSans-Regular.ttf', 20), Colors.WHITE),
            ButtonEvent(gameObject, lambda gameObject: gameObject.quit())
        )
        
        self.create_group("buttons", RestartBtn, MenuBtn, QuitBtn)
        
        
    
    def update(self, events):
        
        
        return super().update(events)