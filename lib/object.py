from typing import Iterable
from random import randint
import pygame as pg

class Color:
    def __init__(self, r, g, b):
        if r > 255:
            r = 255
        elif r < 0:
            r = 0
        if g > 255:
            g = 255
        elif g < 0:
            g = 0
        if b > 255:
            b = 255
        elif b < 0:
            b = 0
        self.r = r
        self.g = g
        self.b = b
    
    def as_iter(self):
        return (self.r, self.g, self.b)

    def as_color(self):
        return pg.Color(self.r, self.g, self.b)

    def reverse(self):
        return Color(255 - self.r, 255 - self.g, 255 - self.b)

    def __add__(self, other):
        if isinstance(other, Color):
            return Color(self.r + other.r, self.g + other.g, self.b + other.b)
        elif isinstance(other, tuple):
            return Color(self.r + other[0], self.g + other[1], self.b + other[2])
        elif isinstance(other, int):
            return Color(self.r + other, self.g + other, self.b + other)
        elif isinstance(other, list):
            return Color(self.r + other[0], self.g + other[1], self.b + other[2])
        elif isinstance(other, dict):
            return Color(self.r + other['r'], self.g + other['g'], self.b + other['b'])
    
    def __sub__(self, other):
        if isinstance(other, Color):
            return Color(self.r - other.r, self.g - other.g, self.b - other.b)
        elif isinstance(other, tuple):
            return Color(self.r - other[0], self.g - other[1], self.b - other[2])
        elif isinstance(other, int):
            return Color(self.r - other, self.g - other, self.b - other)
        elif isinstance(other, list):
            return Color(self.r - other[0], self.g - other[1], self.b - other[2])
        elif isinstance(other, dict):
            return Color(self.r - other['r'], self.g - other['g'], self.b - other['b'])
    
class Colors:
    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)
    ORANGE = Color(255, 165, 0)
    YELLOW = Color(255, 255, 0)
    CYAN = Color(0, 255, 255)
    PURPLE = Color(128, 0, 128)
    
class TextShadowEffect:
    def __init__(self, color_offset: Color, pos_offset: tuple):
        self.color = color_offset.reverse()
        self.offset = pos_offset
    
    def size_with_offset(self, origin_size):
        return (origin_size[0]+abs(self.offset[0]), origin_size[1]+abs(self.offset[1]))

class Text(pg.sprite.Sprite):
    def __init__(self, text:str, font:pg.font.Font, color:Color, center:Iterable=None, text_shadow:TextShadowEffect=None, frame_event:callable=None):
        super().__init__()
        self.image = pg.Surface(font.size(text) if not text_shadow else text_shadow.size_with_offset(font.size(text)), pg.SRCALPHA, 32)
        # self.image = self.image.convert_alpha()
        self.font = font
        self.color = color
        self.text = font.render(text, True, color.as_iter())
        self.text_rect = self.text.get_rect()
        self.text_shadow_obj = text_shadow
        self.text_shadow = None if not text_shadow else font.render(text, True, (color - text_shadow.color).as_iter())
        self.text_shadow_rect = None if not text_shadow else self.text_shadow.get_rect()
        self.rect = self.image.get_rect()
        if center:
            self.rect.centerx = center[0]
            self.rect.centery = center[1]
            self.center = center
        else:
            self.center = None
        self.frame_event = frame_event
        
        if self.text_shadow:
            if text_shadow.offset[0] > 0:
                self.text_rect.x = 0
                self.text_shadow_rect.x = self.rect.width - self.text_shadow_rect.width
            elif text_shadow.offset[0] < 0:
                self.text_rect.x = self.rect.width - self.text_rect.width
                self.text_shadow_rect.x = 0
            elif text_shadow.offset[0] == 0:
                self.text_rect.x = 0
                self.text_shadow_rect.x = 0
            if text_shadow.offset[1] > 0:
                self.text_rect.y = 0
                self.text_shadow_rect.y = self.rect.height - self.text_shadow_rect.height
            elif text_shadow.offset[1] < 0:
                self.text_rect.y = self.rect.height - self.text_rect.height
                self.text_shadow_rect.y = 0
            elif text_shadow.offset[1] == 0:
                self.text_rect.y = 0
                self.text_shadow_rect.y = 0
        else:
            self.text_rect.x = 0
            self.text_rect.y = 0
    
    def render(self, surface:pg.Surface):
        if self.text_shadow:
            self.image.blit(self.text_shadow, self.text_shadow_rect)
        self.image.blit(self.text, self.text_rect)
        if not self.center:
            self.rect = self.image.get_rect(center=surface.get_rect().center)
        surface.blit(self.image, self.rect)
    
    def update(self, events):
        if self.frame_event:
            self.frame_event(events)
            
    def get_another_text(self, text, kill=True, optional_color=None):
        if kill:
            self.kill()
        if optional_color:
            color = optional_color
        else:
            color = self.color
        return Text(text, self.font, color, self.center, self.text_shadow_obj, self.frame_event)
            
class ButtonEvent:
    def __init__(self, gameObject, callback):
        self.game = gameObject
        self.callback = callback
    
    def __call__(self):
        self.callback(self.game)

class Button(pg.sprite.Sprite):
    def __init__(self, size:Iterable, center:Iterable, colors:Iterable[Color], text:Text, click_event:ButtonEvent=None):
        super().__init__()
        self.image = pg.Surface((size[0], size[1]))
        self.image.fill(colors[0].as_iter())
        self.rect = self.image.get_rect(center=center)
        
        self.colors = colors
        self.click_event = click_event
        self.text = text
        
        self.hovered = False
        self.clicked = False
        
        self.disabled = False
    
    def render(self, surface:pg.Surface):
        self.text.render(self.image)
        surface.blit(self.image, self.rect)
    
    def color_update(self):
        if self.disabled:
            self.image.fill((Colors.WHITE - Color(100, 100, 100)).as_iter())
        else:
            if self.hovered:
                if self.clicked:
                    self.image.fill(self.colors[2].as_iter())
                else:
                    self.image.fill(self.colors[1].as_iter())
            else:
                self.image.fill(self.colors[0].as_iter())
    
    def update(self, events):
        mouse_position = pg.mouse.get_pos()
        
        if not self.disabled:
            if self.rect.collidepoint(mouse_position):
                self.hovered = True
                if pg.MOUSEBUTTONDOWN in events:
                    self.clicked = True
                if pg.MOUSEBUTTONUP in events:
                    if self.clicked:
                        self.click_event()
                    self.clicked = False
            else:
                self.clicked = False
                self.hovered = False
        
        self.color_update()

class Player(pg.sprite.Sprite):
    def __init__(self, center, color:Color=Colors.BLUE):
        super().__init__()
        self.image = pg.Surface((10, 10))
        self.image.set_colorkey(Colors.GREEN.as_color())
        self.normal_hitbox_set_x = 10
        self.normal_hitbox_set_y = 10
        self.point_hitbox_expand_x = 20
        self.point_hitbox_expand_y = 20
        
        normal_hitbox = pg.mask.from_surface(self.image)
        point_hitbox = pg.mask.from_surface(self.image)
        point_hitbox.fill()
        
        self.hitboxes = {
            "normal_hitbox": normal_hitbox.scale((self.normal_hitbox_set_x, self.normal_hitbox_set_y)),
            "point_hitbox": point_hitbox.scale((self.normal_hitbox_set_x + self.point_hitbox_expand_x, 
                                                self.normal_hitbox_set_y + self.point_hitbox_expand_y))
        }
        
        self.image.fill(color.as_iter())
        self.rect = self.image.get_rect(center=center)
        self.speed = 3
        self.speed_diag = self.speed / (2**(1/2))
        self.update_per_second = 80
        self.last_update_time = pg.time.get_ticks()
    
    def set_test_hitbox(self, hitbox_name):
        self.mask = self.hitboxes[hitbox_name]
    
    def render(self, surface:pg.Surface):
        surface.blit(self.image, self.rect)
        # Hitbox Visualization for debugging
        # surface.blit(self.hitboxes["point_hitbox"].to_surface(setcolor=Colors.GREEN.as_iter()), (self.rect.topleft[0]-(self.point_hitbox_expand_x/2), 
        #                                                                                          self.rect.topleft[1]-(self.point_hitbox_expand_y/2)))
        # surface.blit(self.hitboxes["normal_hitbox"].to_surface(setcolor=Colors.RED.as_iter()), self.rect)
    
    def update(self, events):
        if pg.time.get_ticks() - self.last_update_time < 1000 / self.update_per_second:
            return
        self.last_update_time = pg.time.get_ticks()
        keys = pg.key.get_pressed()
        if ((not keys[pg.K_w] and keys[pg.K_s]) or (keys[pg.K_w] and not keys[pg.K_s])) \
            and ((not keys[pg.K_a] and keys[pg.K_d]) or (keys[pg.K_a] and not keys[pg.K_d])):
            speed = self.speed_diag
        else:
            speed = self.speed
        
        if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
            speed *= 2
        
        if keys[pg.K_w]:
            self.rect.y -= speed
        if keys[pg.K_s]:
            self.rect.y += speed
        if keys[pg.K_a]:
            self.rect.x -= speed
        if keys[pg.K_d]:
            self.rect.x += speed

class Enemy(pg.sprite.Sprite):
    def __init__(self, x_change, y_change, target_pos, start_x: bool, start_full: bool, screen_size: int, color:Color=Colors.RED):
        super().__init__()
        self.image = pg.Surface((10, 10))
        self.image.set_colorkey(Colors.GREEN.as_color())
        self.mask = pg.mask.from_surface(self.image)
        self.image.fill(color.as_iter())
        self.change_multiply = 2
        
        self.x_change = x_change  # assume x_change and y_change are both not 0
        self.y_change = y_change
        if self.x_change == 0:
            self.x_change = -1 if randint(0, 1) == 0 else 1
        if self.y_change == 0:
            self.y_change = -1 if randint(0, 1) == 0 else 1
            
        self.tilt = self.y_change / self.x_change
        
        self.x_function = lambda x: self.tilt * (x - target_pos[0]) + target_pos[1]
        self.y_function = lambda y: (y - target_pos[1]) / self.tilt + target_pos[0]
        
        if start_x:
            if start_full:
                start_pos = (screen_size[0], self.x_function(screen_size[0]))
                self.end_pos = (0, self.x_function(0))
                self.x_change = -self.x_change
                self.y_change = -self.y_change
            else:
                start_pos = (0, self.x_function(0))
                self.end_pos = (screen_size[0], self.x_function(screen_size[0]))
        else:
            if start_full:
                start_pos = (self.y_function(screen_size[1]), screen_size[1])
                self.end_pos = (self.y_function(0), 0)
                self.x_change = -self.x_change
                self.y_change = -self.y_change
            else:
                start_pos = (self.y_function(0), 0)
                self.end_pos = (self.y_function(screen_size[1]), screen_size[1])
        
        self.rect = self.image.get_rect(center=start_pos)
        
        self.counted = False
        
        self.last_update_time = pg.time.get_ticks()
        self.update_per_second = 60
    
    def f(self, x):
        return self.tilt * (x - self.target_pos[0]) + self.target_pos[1]
    
    def update(self, events):
        if pg.time.get_ticks() - self.last_update_time < 1000 / self.update_per_second:
            return
        self.last_update_time = pg.time.get_ticks()
        self.rect.x += self.x_change * self.change_multiply
        self.rect.y += self.y_change * self.change_multiply
        if (self.rect.x, self.rect.y) == self.end_pos:
            self.kill()
            
    
    def render(self, surface:pg.Surface):
        surface.blit(self.image, self.rect)

class Star(pg.sprite.Sprite):
    def __init__(self, x, y, color:Color=Colors.WHITE):
        super().__init__()
        self.image = pg.Surface((2, 2))
        self.image.set_alpha(0)
        self.image.fill(color.as_iter())
        self.rect = self.image.get_rect(center=(x, y))
        
        self.born_time = pg.time.get_ticks()
        self.live_time = randint(1000, 5000)
    
    def update(self, events):
        living_time = pg.time.get_ticks() - self.born_time
        
        if pg.time.get_ticks() - self.born_time > self.live_time:
            self.kill()
        else:
            # alpha animation
            # 0 to 255
            if living_time < self.live_time / 2:
                self.image.set_alpha(255 * (living_time / (self.live_time / 2)))
            else:
                self.image.set_alpha(255 * (1 - (living_time - self.live_time / 2) / (self.live_time / 2)))
    
    def render(self, surface):
        surface.blit(self.image, self.rect)

class NumberInputBox(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, colors: Iterable[Color], font):
        super().__init__()
        self.image = pg.Surface((width+2, height+2))
        self.rect = self.image.get_rect(center=(x, y))
        
        self.colors = {
            "normal": {
                "background": colors[0],
                "background_border": colors[1],
                "text": colors[2],
            },
            "hover": {
                "background": colors[3],
                "background_border": colors[4],
                "text": colors[5],
            },
            "pressed": {
                "background": colors[6],
                "background_border": colors[7],
                "text": colors[8],
            },
            "active": {
                "background": colors[9],
                "background_border": colors[10],
                "text": colors[11],
            }
        }
        self.image.fill(self.colors["normal"]["background"].as_iter())
        
        self.text = ""
        self.font = font
        self.limit = 5
        
        self.hovered = False
        self.pressed = False
        self.activated = False
    
    def update(self, events):
        if self.rect.collidepoint(pg.mouse.get_pos()):
            self.hovered = True
            if not self.pressed and pg.mouse.get_pressed()[0]:
                self.pressed = True
            elif self.pressed and not pg.mouse.get_pressed()[0]:
                self.pressed = False
                self.activated = True
        elif self.activated and pg.mouse.get_pressed()[0]:
            self.activated = False
            self.pressed = False
            self.hovered = False
        else:
            self.hovered = False
            self.pressed = False
        
        if self.activated:  # key input event
            if pg.KEYDOWN in events:
                if len(self.get_text()) < self.limit:
                    if pg.key.get_pressed()[pg.K_1]:
                        self.text += "1"
                    if pg.key.get_pressed()[pg.K_2]:
                        self.text += "2"
                    if pg.key.get_pressed()[pg.K_3]:
                        self.text += "3"
                    if pg.key.get_pressed()[pg.K_4]:
                        self.text += "4"
                    if pg.key.get_pressed()[pg.K_5]:
                        self.text += "5"
                    if pg.key.get_pressed()[pg.K_6]:
                        self.text += "6"
                    if pg.key.get_pressed()[pg.K_7]:
                        self.text += "7"
                    if pg.key.get_pressed()[pg.K_8]:
                        self.text += "8"
                    if pg.key.get_pressed()[pg.K_9]:
                        self.text += "9"
                    if pg.key.get_pressed()[pg.K_0]:
                        self.text += "0"
                if pg.key.get_pressed()[pg.key.key_code("backspace")]:
                    self.text = self.text[:-1]
    
    def render(self, surface):
        if self.activated:
            self.image.fill(self.colors["active"]["background"].as_iter())
        elif self.pressed:
            self.image.fill(self.colors["pressed"]["background"].as_iter())
        elif self.hovered:
            self.image.fill(self.colors["hover"]["background"].as_iter())
        else:
            self.image.fill(self.colors["normal"]["background"].as_iter())

        if self.activated:
            pg.draw.rect(self.image, self.colors["active"]["background_border"].as_iter(), (0, 0, self.rect.width, self.rect.height), 1)
        elif self.pressed:
            pg.draw.rect(self.image, self.colors["pressed"]["background_border"].as_iter(), (0, 0, self.rect.width, self.rect.height), 1)
        elif self.hovered:
            pg.draw.rect(self.image, self.colors["hover"]["background_border"].as_iter(), (0, 0, self.rect.width, self.rect.height), 1)
        else:
            pg.draw.rect(self.image, self.colors["normal"]["background_border"].as_iter(), (0, 0, self.rect.width, self.rect.height), 1)
        
        text = self.font.render(self.text, True, self.colors["normal"]["text"].as_iter())
        self.image.blit(text, (self.rect.width / 2 - text.get_width() / 2, self.rect.height / 2 - text.get_height() / 2))
        surface.blit(self.image, self.rect)
    
    def get_text(self):
        return self.text
