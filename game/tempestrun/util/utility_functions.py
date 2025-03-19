import math
import os
import pathlib
import sys
from typing import Union, List

import pygame

# import config

pygame.init()


def distance(p1: Union[tuple, list], p2: Union[tuple, list]) -> float:
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def get_display_resolution():   # -> tuple[int, int]:
    display_width: int = pygame.display.Info().current_w
    display_height: int = pygame.display.Info().current_h
    return display_width, display_height


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, str(pathlib.Path(relative_path)))


def lerp(a: float, v1, v2, restrict_between=True):
    """Linearly interpolates between v1 and v2 based on a's value (from 0 to 1)

    example: a=0.75, v1=0, v2=4 --> 3.0
    """
    if a <= 0 and restrict_between:
        return v1
    elif a >= 1 and restrict_between:
        return v2
    else:
        return a * (v2 - v1) + v1


def abs_angle_between_angles(a1_deg, a2_deg):
    """
    :return: (angle_between, whether the shortest distance is in the positive direction)
    """
    phi = abs(a2_deg - a1_deg) % 360
    return (360 - phi, False) if phi > 180 else (phi, True)


def map_from_interval_to_interval(val: float, interval1: List[float], interval2: List[float]):
    """Linearly maps a value from one interval to another

    example: val=2, interval1=[0, 4], interval2=[0, 10] -> 5
    """
    a = (val - interval1[0]) / (interval1[1] - interval1[0])
    return lerp(a, interval2[0], interval2[1], restrict_between=False)


class SpriteSheet:
    def __init__(self, img_file_name: Union[str, pygame.Surface], sprite_qty, row, col, color_key=None, flipped=False, scale_factor=1):
        self.scale_factor = scale_factor
        self.is_flipped = flipped
        self.sheet = pygame.image.load(img_file_name) if type(img_file_name) is str else img_file_name
        self.row = row
        self.col = col
        self.w = self.sheet.get_width() // self.col
        self.h = self.sheet.get_height() // self.row
        self.color_key = color_key
        self.sprite_qty = sprite_qty
        self.sprites = []

    def get_sprite_at_pos(self, x, y):
        img = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        img.blit(self.sheet, (0, 0), pygame.Rect(x, y, self.w, self.h))
        img = pygame.transform.scale(img, (img.get_width() * self.scale_factor, img.get_height() * self.scale_factor))
        if self.color_key is not None:
            img.set_colorkey(self.color_key)
        if self.is_flipped:
            return pygame.transform.flip(img, True, False)
        else:
            return img

    def get_images(self):
        c = 0
        images = []
        for i in range(self.row * self.col):
            c += 1
            if c > self.sprite_qty:
                break
            sprite = self.get_sprite_at_pos((i % self.col) * self.w, i % self.row * self.h)
            images.append(sprite)
        return images
