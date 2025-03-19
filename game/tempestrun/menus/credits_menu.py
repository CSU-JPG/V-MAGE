import random

import pygame

import rendering.neon as neon
import keybinds
from main import GameMode, GameLoop
import util.fonts as fonts
import config


class CreditsMenuMode(GameMode):

    def __init__(self, loop: GameLoop, prev_menu: GameMode):
        super().__init__(loop)
        self.prev_menu = prev_menu

        self.selected_option_idx = 0
        self.options = [
            ("ghast", None),
            ("tank king", None),
            ("bydariogamer", None),
            ("spooky", None)
        ]

        self.n_squares = 25
        self.squares = [self._generate_square() for _ in range(self.n_squares)]  # format -> [x, y, angle, speed]

        self.title_font = fonts.get_font(config.FontSize.title)
        self.option_font = fonts.get_font(config.FontSize.option)
        self.info_font = fonts.get_font(config.FontSize.info)

    def _generate_square(self):
        screen_w, screen_h = pygame.display.get_surface().get_size()
        return [random.randint(0, screen_w),  # x position
                screen_h + 25,                # y position
                random.randint(0, 360),       # angle
                random.randint(2, 10) / 2 * random.choice([-1, 1])]  # speed

    @staticmethod
    def get_square_points(x, y, angle, size=50):
        # points of a square rotated at an angle with respect to it's center
        points = [
            [-size // 2, - size // 2],
            [size // 2, - size // 2],
            [size // 2, size // 2],
            [-size // 2, size // 2]
        ]
        points = [pygame.Vector2(i[0], i[1]).rotate(angle) for i in points]
        points = [[x + i[0], y + i[1]] for i in points]
        return points

    def on_mode_start(self):
        # TODO song
        pass

    def exit_pressed(self):
        self.loop.set_mode(self.prev_menu)

    def update(self, dt, events):
        for i in self.squares:
            i[2] += i[3] * dt * 100
            i[1] -= abs(i[3]) * dt * 100
        self.squares = [s for s in self.squares if s[1] > -50]  # purge squares that fell off the top of the screen

        while len(self.squares) < self.n_squares:
            self.squares.append(self._generate_square())

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in keybinds.MENU_LEFT:
                    
                    self.selected_option_idx = (self.selected_option_idx - 1) % len(self.options)
                elif e.key in keybinds.MENU_RIGHT:
                    
                    self.selected_option_idx = (self.selected_option_idx + 1) % len(self.options)
                if e.key in keybinds.MENU_UP:
                    
                    self.selected_option_idx = (self.selected_option_idx - 2) % len(self.options)
                elif e.key in keybinds.MENU_DOWN:
                    
                    self.selected_option_idx = (self.selected_option_idx + 2) % len(self.options)
                elif e.key in keybinds.MENU_CANCEL:
                    
                    self.exit_pressed()
                    return

    def draw_to_screen(self, screen):
        screen.fill((0, 0, 0))

        for i in self.squares:
            pygame.draw.lines(screen, (0, 255, 0), True, self.get_square_points(i[0], i[1], i[2]))
        screen_size = screen.get_size()
        title_surface = self.title_font.render('CREDITS', False, neon.WHITE)

        title_size = title_surface.get_size()
        title_y = screen_size[1] // 4 - title_size[1] // 2
        screen.blit(title_surface, dest=(screen_size[0] // 2 - title_size[0] // 2,
                                         title_y))

        option_y = max(int(screen_size[1] * 0.4), title_y + title_size[1])
        msg = ''
        for i in range(len(self.options)):
            option_text = self.options[i][0]
            is_selected = i == self.selected_option_idx
            color = neon.WHITE if not is_selected else neon.RED
            if is_selected:
                if i == 0:
                    msg = 'programming'
                elif i == 1:
                    msg = 'programming'
                elif i == 2:
                    msg = 'programming'
                elif i == 3:
                    msg = 'sfx & bgm'
            option_surface = self.option_font.render(option_text.upper(), False, color)
            option_size = option_surface.get_size()
            option_x = screen_size[0] // 6 + (screen_size[0] - 2 * screen_size[0] // 6) // 2 * (i % 2 + 0.5) - option_size[0] // 2
            screen.blit(option_surface, dest=(option_x, option_y))
            msg_surf = self.info_font.render(msg.upper(), False, neon.WHITE)
            screen.blit(msg_surf, msg_surf.get_rect(center=(screen_size[0] // 2, screen_size[1] * 3 / 4)))
            if i == 1:
                option_y += option_size[1] + 20
