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

class Text(pg.sprite.Sprite):
    def __init__(self, text:str, font:pg.font.Font, color:Color, center:Iterable=None, frame_event:callable=None):
        super().__init__()
        self.image = pg.Surface(font.size(text), pg.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.text = font.render(text, True, color.as_iter())
        self.rect = self.image.get_rect()
        if center:
            self.rect.centerx = center[0]
            self.rect.centery = center[1]
            self.center = center
        else:
            self.center = None
        self.frame_event = frame_event
    
    def render(self, surface:pg.Surface):
        self.image.blit(self.text, (0, 0))
        if not self.center:
            self.rect = self.image.get_rect(center=surface.get_rect().center)
        surface.blit(self.image, self.rect)
    
    def update(self, events):
        if self.frame_event:
            self.frame_event(events)
            
            
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
        self.image.fill(color.as_iter())
        self.rect = self.image.get_rect(center=center)
        self.speed = 3
        self.speed_diag = self.speed / (2**(1/2))
    
    def render(self, surface:pg.Surface):
        surface.blit(self.image, self.rect)
    
    def update(self, events):
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
    def __init__(self, x_change, y_change, target_pos, start_x: bool, start_y: bool, screen_size: int, color:Color=Colors.RED):
        super().__init__()
        self.image = pg.Surface((10, 10))
        self.image.fill(color.as_iter())
        self.change_multiply = 2
        
        self.x_change = x_change  # assume x_change and y_change are both not 0
        self.y_change = y_change
        if self.x_change == 0:
            self.x_change = -1 if randint(0, 1) == 0 else 1
        if self.y_change == 0:
            self.y_change = -1 if randint(0, 1) == 0 else 1
            
        self.tilt = self.y_change / self.x_change
        
        x_function = lambda x: self.tilt * (x - target_pos[0]) + target_pos[1]
        y_function = lambda y: (y - target_pos[1]) / self.tilt + target_pos[0]
        
        if start_x:
            if start_y:
                start_pos = (screen_size[0], x_function(screen_size[0]))
                self.x_change = -self.x_change
                self.y_change = -self.y_change
            else:
                start_pos = (0, x_function(0))
        else:
            if start_y:
                start_pos = (y_function(screen_size[1]), screen_size[1])
                self.x_change = -self.x_change
                self.y_change = -self.y_change
            else:
                start_pos = (y_function(0), 0)
        
        self.rect = self.image.get_rect(center=start_pos)
    
    def f(self, x):
        return self.tilt * (x - self.target_pos[0]) + self.target_pos[1]
    
    def update(self, events):
        self.rect.x += self.x_change * self.change_multiply
        self.rect.y += self.y_change * self.change_multiply
    
    def render(self, surface:pg.Surface):
        surface.blit(self.image, self.rect)
