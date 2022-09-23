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
            
    def set_text(self, text):
        self.text = self.font.render(text, True, self.color.as_iter())
        self.text_shadow = None if not self.text_shadow_obj else self.font.render(text, True, (self.color - self.text_shadow_obj.color).as_iter())
        self.rect.width = self.font.size(text)[0] if not self.text_shadow_obj else self.text_shadow_obj.size_with_offset(self.font.size(text))[0]
        self.rect.height = self.font.size(text)[1] if not self.text_shadow_obj else self.text_shadow_obj.size_with_offset(self.font.size(text))[1]
            
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
    
    def render(self, surface:pg.Surface):
        self.text.render(self.image)
        surface.blit(self.image, self.rect)
    
    def color_update(self):
        if self.hovered:
            if self.clicked:
                self.image.fill(self.colors[2].as_iter())
            else:
                self.image.fill(self.colors[1].as_iter())
        else:
            self.image.fill(self.colors[0].as_iter())
    
    def update(self, events):
        mouse_position = pg.mouse.get_pos()
        
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
