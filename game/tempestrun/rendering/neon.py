from math import ceil
from typing import List, Iterable
import pygame
import cv2
import numpy
import config


# taken from https://www.coolneon.com/wp-content/uploads/2014/11/color-chart.png
CYAN = pygame.Color(0, 255, 255)
BLUE = pygame.Color(0, 84, 247)
TEAL = pygame.Color(0, 161, 115)
LIME = pygame.Color(123, 255, 0)
YELLOW = pygame.Color(251, 208, 0)
ORANGE = pygame.Color(255, 70, 0)
RED = pygame.Color(231, 0, 0)
PURPLE = pygame.Color(154, 0, 154)
PINK = pygame.Color(253, 17, 96)
WHITE = pygame.Color(220, 220, 255)
BLACK = pygame.Color(0, 0, 0)

ALL_COLORS = [CYAN, BLUE, TEAL, LIME, YELLOW, ORANGE, RED, PURPLE, PINK, WHITE]


class NeonLine:
    """
    Represents a line NeonRenderer can draw.
    """
    def __init__(self,
                 points: List[pygame.Vector2],
                 width: int,
                 color: pygame.Color,
                 inner_color: pygame.Color = None,
                 inner_width: int = None):

        self.vector_points = points
        # x and y are flipped intentionally... this is what cv2 understands, don't ask me~
        self.np_points = numpy.array([[round(p.y), round(p.x)] for p in points], numpy.int32).reshape((-1, 1, 2))
        self.width = width
        self.inner_width = inner_width or 1
        self.inner_color = inner_color or WHITE
        self.color = color

    @staticmethod
    def convert_line2ds_to_neon_lines(line2ds) -> List['NeonLine']:
        # why are there two nearly identical line classes, you ask? i f-d up
        # anyways this method converts a list of Line2Ds into NeonLines~
        return [NeonLine([l.p1, l.p2], l.width, l.color, inner_color=l.inner_color) for l in line2ds]


class NeonRenderer:
    """
    A class that renders lines with a cool neon effect.
    """

    def __init__(self,
                 ambient_bloom_kernel=(15, 15),
                 mid_tone_bloom_kernel=(3, 3),
                 highlight_bloom_kernel=None):
        self.ambient_bloom_kernel = ambient_bloom_kernel
        self.mid_tone_bloom_kernel = mid_tone_bloom_kernel
        self.highlight_bloom_kernel = highlight_bloom_kernel
        self.darkness_factor = 1  # this is pretty krangled now, off by default~

        self._buf = None  # a buffer for intermediate drawing operations

    def draw_lines(self, surface: pygame.Surface, lines: Iterable[NeonLine], extra_darkness_factor=1):
        """Draws lines with a fancy neon effect.
        :param surface: the surface to draw them onto
        :param lines: the lines to draw
        :param extra_darkness_factor: a value from 0 to 1 that will control the 'extra darkness' of the lines (0 being completely dark).
        """
        if not config.Debug.use_neon:
            for line in lines:
                pygame.draw.lines(surface, line.color, False, line.vector_points, width=int(line.width))
            return

        if self._buf is None or (self._buf.shape[0], self._buf.shape[1]) != surface.get_size():
            self._buf = pygame.surfarray.array3d(surface)

        # # fill screen with black
        self._buf[...] = 0

        # Ghast's Neon Line Drawing AlgorithmTM

        # 1st pass, draw large, dark, faint glow around line
        for line in lines:
            self.polylines(self._buf, [line.np_points], False, line.color.lerp((0, 0, 0), 0.15), line.width)
        self._blur(self._buf, self.ambient_bloom_kernel)

        # 2nd pass, draw smaller, brighter glow
        for line in lines:
            self.polylines(self._buf, [line.np_points], False, line.color, line.inner_width)
        self._blur(self._buf, self.mid_tone_bloom_kernel)

        # 3rd pass, draw anti-aliased highlight
        for line in lines:
            self.polylines(self._buf, [line.np_points], False, line.inner_color, line.inner_width, lineType=cv2.LINE_AA)
        self._blur(self._buf, self.highlight_bloom_kernel)

        # post processing effects
        self._darken(self._buf, self.darkness_factor * extra_darkness_factor)

        pygame.surfarray.blit_array(surface, self._buf)

    def polylines(self, array, pts, connected, color, width, lineType=cv2.LINE_4):
        """calls cv2.polylines with the given params.
        The only reason this method is split off like this is to make things easier to profile.
        """
        cv2.polylines(array, pts, connected, color, width, lineType=lineType)

    def _blur(self, array, kernel):
        """blurs the image using cv2.blur
        The only reason this method is split off like this is to make things easier to profile.
        """
        if kernel is not None:
            cv2.blur(array, kernel, dst=array)

    def _darken(self, array, darkness_factor):
        """darkens the image
        :param darkness_factor: a value from 0 to 1 that determines how dark it will be
        """
        if darkness_factor < 1:
            # apparently multiplying by a float is too expensive (ask bydario~)
            denominator = 100
            numerator = int(darkness_factor * denominator)
            array[...] = array // denominator * numerator


if __name__ == "__main__":
    import random

    W, H = SIZE = (600, 400)
    N = 50

    def rand_pt():
        return pygame.Vector2(random.randint(0, W), random.randint(0, H))

    lines = []
    for _ in range(N):
        lines.append(NeonLine(
            [rand_pt(), rand_pt()],
            random.randint(1, 1),
            random.choice(ALL_COLORS)))

    # values determined empirically
    big_bloom = round(25 * W / 300)
    big_bloom = big_bloom + (1 - big_bloom % 2)  # gotta be odd
    mid_bloom = round(3 * W / 300)
    mid_bloom = mid_bloom + (1 - mid_bloom % 2)  # gotta be odd
    renderer = NeonRenderer(ambient_bloom_kernel=(big_bloom, big_bloom),
                            mid_tone_bloom_kernel=(mid_bloom, mid_bloom))

    pygame.init()
    pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)

    clock = pygame.time.Clock()
    t = 0
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                raise SystemExit

        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))

        renderer.draw_lines(screen, lines)

        pygame.display.flip()
        t += 1
        if t % 60 == 59:
            pygame.display.set_caption("FPS: {:.1f}".format(clock.get_fps()))
        clock.tick(60)

