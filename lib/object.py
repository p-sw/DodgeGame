from typing import Iterable
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
        self.text = font.render(text, True, color.as_iter())  # text, antialiasing, color
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
            
class Button(pg.sprite.Sprite):
    def __init__(self, size:Iterable, center:Iterable, colors:Iterable[Color], text:Text, click_event:callable=None):
        super().__init__()
        self.image = pg.Surface((size[0], size[1]))
        self.image.fill(colors[0].as_iter())
        self.rect = self.image.get_rect(center=center)
        # #
        self.colors = colors # 0: normal, 1: hovered, 2: clicked
        self.click_event = click_event
        self.text = text
        # Predefine status variables
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