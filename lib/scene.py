from typing import Iterable
from random import randint
from pathlib import Path
from os import path
import pygame as pg

from lib.object import Text, Color, Button, Colors, ButtonEvent, TextShadowEffect
from lib.object import Player, Enemy

BASEDIR = Path(__file__).parent.parent.absolute()

def font_located(fontname):
    return path.join((BASEDIR, 'assets', 'font', fontname+'.ttf'))

class Scene:
    def __init__(self):
        self.groups = {}
        self.raws = {}
        
    def add_item(self, name, *sprites:Iterable[pg.sprite.Sprite]):
        self.groups[name].add(sprites)
    
    def add_raw_item(self, item, center, name):
        self.raws[name] = [item, center]
    
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
        
        for item,center in self.raws.values():
            screen.blit(item, item.get_rect(center=center))
    
    def inherit_groups(self, *group_names):
        return {name: self.groups[name] for name in group_names}

class MenuScene(Scene):
    def __init__(self, gameObject, data):
        super().__init__()
        self.screen_color = Colors.WHITE.as_iter()
        
        title_font = pg.font.Font(font_located('BlackHanSans-Regular'), 40)
        button_font = pg.font.Font(font_located('ONE Mobile Bold'), 30)
        title = Text("부평고 2022 코딩동아리 게임", 
                     title_font, 
                     Colors.ORANGE,
                     (
                         gameObject.screen.get_width() / 2, 
                         gameObject.screen.get_height() / 6
                     ),
                     TextShadowEffect(Colors.ORANGE + Color(20, 20, 20), (2, 2)))
        self.create_group("title", title)
        
        BUTTON_COLOR = [
            Colors.ORANGE,
            Colors.RED,
            Colors.RED - Color(100, 0, 0)
        ]
        
        start_button = Button(
            (200, 50),
            (
                gameObject.screen.get_width() / 2,
                gameObject.screen.get_height() / 8 * 5 - 40
            ),
            BUTTON_COLOR,
            Text("시작하기", button_font, Colors.WHITE),
            ButtonEvent(gameObject, lambda gameObject: gameObject.change_scene("game", GameScene))
        )
        quit_button = Button(
            (200, 50),
            (
                gameObject.screen.get_width() / 2,
                gameObject.screen.get_height() / 8 * 5 + 40
            ),
            BUTTON_COLOR,
            Text("종료하기", button_font, Colors.WHITE),
            ButtonEvent(gameObject, lambda gameObject: gameObject.quit())
        )
        self.create_group("buttons", start_button, quit_button)

class GameScene(Scene):
    def __init__(self, gameObject, data):
        self.game = gameObject
        super().__init__()
        self.started_time = pg.time.get_ticks()
        self.screen_color = Colors.WHITE.as_iter()
        
        self.player = Player((gameObject.screen.get_width() // 2, gameObject.screen.get_height() // 2), Colors.BLUE)
        self.create_group("player", self.player)
        
        self.score_display_font = pg.font.Font(font_located('INVASION2000'), 60)
        self.score_displayer = self.score_display_font.render("0", True, Colors.ORANGE.as_iter())
        self.add_raw_item(self.score_displayer, (gameObject.screen.get_width() / 2, gameObject.screen.get_height() / 8),"score_displayer")
        
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
                self.game.change_scene("result", ResultScene, {"inheritGroups": self.inherit_groups("enemy"), "elapsedTime": elapsed_time, "score": self.score, "totalScore": elapsed_time + self.score})
            elif point_hit(item) and not item.counted:
                item.counted = True
                self.score += 2000
        
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
        
        self.raws["score_displayer"][0] = self.score_display_font.render(str(elapsed_time), True, Colors.ORANGE.as_iter())
        
        super().update(events)

class ResultScene(Scene):
    def __init__(self, gameObject, data):
        super().__init__()
        self.scene_start_time = pg.time.get_ticks()
        self.last_update_time = self.scene_start_time
        self.screen_color = Colors.WHITE.as_iter()
        self.groups = data["inheritGroups"]
        self.screen = gameObject.screen
        
        self.score = data["score"]
        self.elapsed_time = data["elapsedTime"]
        self.total_score = data["totalScore"]
        
        self.anim_current_score = 0
        self.anim_current_elapsed_time = 0
        self.anim_current_total_score = 0
        
        button_font = pg.font.Font(font_located('One Mobile Bold'), 30)
        
        title = Text(
            "Game Over", 
            pg.font.Font(font_located('BlackHanSans-Regular'), 40), 
            Colors.ORANGE, 
            (gameObject.screen.get_width() / 2, gameObject.screen.get_height() / 5),
            TextShadowEffect(Colors.ORANGE + Color(20, 20, 20), (2, 2)))
        self.create_group("title", title)
        
        BUTTON_COLOR = [
            Colors.ORANGE,
            Colors.RED,
            Colors.RED - Color(100, 0, 0)
        ]
        
        self.score_displayer_font = pg.font.Font(font_located('INVASION2000'), 40)
        self.score_displayer = self.score_displayer_font.render(str(self.score), True, Colors.ORANGE.as_iter())
        
        self.score_comment_font = pg.font.Font(font_located('BlackHanSans-Regular'), 40)
        self.score_comment_overall = self.score_comment_font.render("총 점수", True, (Colors.RED - Color(50, 0, 0)).as_iter())
        self.score_comment_time = self.score_comment_font.render("시간 점수", True, (Colors.RED - Color(50, 0, 0)).as_iter())
        self.score_comment_barely_missed = self.score_comment_font.render("액션 점수", True, (Colors.RED - Color(50, 0, 0)).as_iter())
        
        self.score_splitted_time = self.score_displayer_font.render("0", True, Colors.ORANGE.as_iter())
        self.score_splitted_barely_missed = self.score_displayer_font.render("0", True, Colors.ORANGE.as_iter())
        
        self.add_raw_item(self.score_displayer, (gameObject.screen.get_width() / 2, gameObject.screen.get_height() / 5 + 100), "score_displayer")
        self.add_raw_item(self.score_comment_overall, (gameObject.screen.get_width() / 2, gameObject.screen.get_height() / 5 + 70), "score_comment_overall")
        self.add_raw_item(self.score_comment_time, (gameObject.screen.get_width() / 4, gameObject.screen.get_height() / 5 + 170), "score_comment_time")
        self.add_raw_item(self.score_comment_barely_missed, (gameObject.screen.get_width() / 4 * 3, gameObject.screen.get_height() / 5 + 170), "score_comment_barely_missed")
        self.add_raw_item(self.score_splitted_time, (gameObject.screen.get_width() / 4, gameObject.screen.get_height() / 5 + 200), "score_splitted_time")
        self.add_raw_item(self.score_splitted_barely_missed, (gameObject.screen.get_width() / 4 * 3, gameObject.screen.get_height() / 5 + 200), "score_splitted_barely_missed")
        
        self.score_animation_time_delay = 50
        self.score_animation_barely_missed_delay = 50
        self.score_animation_time_chunk = 1000
        self.score_animation_barely_missed_chunk = 1000
        
        self.animation_finished = False
        self.score_time_animation_finished = False
        self.score_barely_missed_animation_finished = False
        
        self.RestartBtn = Button(
            (200, 50),
            (gameObject.screen.get_width() / 2, gameObject.screen.get_height() / 8 * 5 - 40),
            BUTTON_COLOR,
            Text("다시하기", button_font, Colors.WHITE),
            ButtonEvent(gameObject, lambda gameObject: gameObject.change_scene("game", GameScene))
        )
        
        self.MenuBtn = Button(
            (200, 50),
            (gameObject.screen.get_width() / 2, gameObject.screen.get_height() / 8 * 5 + 40),
            BUTTON_COLOR,
            Text("메뉴로", button_font, Colors.WHITE),
            ButtonEvent(gameObject, lambda gameObject: gameObject.change_scene("menu", MenuScene))
        )
        
        self.QuitBtn = Button(
            (200, 50),
            (gameObject.screen.get_width() / 2, gameObject.screen.get_height() / 8 * 5 + 120),
            BUTTON_COLOR,
            Text("종료하기", button_font, Colors.WHITE),
            ButtonEvent(gameObject, lambda gameObject: gameObject.quit())
        )
        
        # self.create_group("buttons", RestartBtn, MenuBtn, QuitBtn)
    
    def update(self, events):
        super().update(events)
        from_last_time = pg.time.get_ticks() - self.last_update_time
        
        if not self.animation_finished:
            if not self.score_time_animation_finished:
                if from_last_time >= self.score_animation_time_delay:
                    if self.anim_current_elapsed_time + self.score_animation_time_chunk > self.elapsed_time:
                        self.score_time_animation_finished = True
                        overflowed = self.score_animation_time_chunk - ((self.anim_current_elapsed_time + self.score_animation_time_chunk) - self.elapsed_time)
                        self.anim_current_elapsed_time += overflowed
                        self.anim_current_total_score += overflowed
                        self.last_update_time = pg.time.get_ticks()
                    else:
                        self.anim_current_elapsed_time += self.score_animation_time_chunk
                        self.anim_current_total_score += self.score_animation_time_chunk
                        self.last_update_time = pg.time.get_ticks()
            elif not self.score_barely_missed_animation_finished:
                if from_last_time >= self.score_animation_barely_missed_delay:
                    if self.anim_current_score + self.score_animation_barely_missed_chunk > self.score:
                        self.score_barely_missed_animation_finished = True
                        overflowed = self.score_animation_barely_missed_chunk - ((self.anim_current_score + self.score_animation_barely_missed_chunk) - self.score)
                        self.anim_current_score += overflowed
                        self.anim_current_total_score += overflowed
                        self.last_update_time = pg.time.get_ticks()
                    else:
                        self.anim_current_score += self.score_animation_barely_missed_chunk
                        self.anim_current_total_score += self.score_animation_barely_missed_chunk
                        self.last_update_time = pg.time.get_ticks()
            else:
                self.animation_finished = True
                self.create_group("buttons", self.RestartBtn, self.MenuBtn, self.QuitBtn)
                
        self.raws["score_displayer"][0] = self.score_displayer_font.render(f"{self.anim_current_total_score}", True, Colors.ORANGE.as_iter())
        
        self.raws["score_splitted_time"][0] = self.score_displayer_font.render(f"{self.anim_current_elapsed_time}", True, Colors.ORANGE.as_iter())
        
        self.raws["score_splitted_barely_missed"][0] = self.score_displayer_font.render(f"{self.anim_current_score}", True, Colors.ORANGE.as_iter())
