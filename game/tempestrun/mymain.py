import pygame

import keybinds
import rendering.neon as neon
import config
import util.profiling as profiling
import util.fonts as fonts
import rendering.levelbuilder3d as levelbuilder3d
import gameplay.highscores as highscores
import util.utility_functions as utils


TARGET_FPS = config.Display.fps if not config.Debug.fps_test else -1


class GameLoop:

    def __init__(self):
        self.running = True
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.get_surface()
        import gameplay.gamestuff  # shh don't tell pylint about this
        self.current_mode = gameplay.gamestuff.GameplayMode(self)
        self.current_mode.on_mode_start()

    def set_mode(self, next_mode):
        if self.current_mode != next_mode:
            self.current_mode.on_mode_end()
        self.current_mode = next_mode
        self.current_mode.on_mode_start()

    def start(self):
        dt = 0
        while self.running:
            events = []
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                    return
                else:
                    # collect all the events so we can pass them into the current game mode.
                    events.append(e)

                # global keybinds
                if e.type == pygame.KEYDOWN:
                    if e.key in keybinds.TOGGLE_NEON:
                        config.Debug.use_neon = not config.Debug.use_neon
                    if e.key in keybinds.TOGGLE_PROFILER:
                        profiling.get_instance().toggle()
            cur_mode = self.current_mode

            cur_mode.update(dt, events)
            
            cur_mode.draw_to_screen(self.screen)
            

            pygame.display.flip()

            if config.Debug.fps_test:
                pygame.display.set_caption(f"{config.Display.title} {int(self.clock.get_fps())} FPS")
            
            self.clock.tick(TARGET_FPS)
            dt = 0.0165
            
            if self.current_mode.player.is_dead():
                self.running = False


class GameMode:

    def __init__(self, loop: GameLoop):
        self.loop: GameLoop = loop

    def on_mode_start(self):
        """Called when mode becomes active"""
        pass

    def on_mode_end(self):
        """Called when mode becomes inactive"""
        pass

    def update(self, dt, events):
        pass

    def draw_to_screen(self, screen):
        pass


def create_or_recreate_window():
    size = config.Display.width, config.Display.height

    pygame.display.set_mode(size, pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption(config.Display.title)
    pygame.display.set_icon(pygame.image.load(utils.resource_path("game/tempestrun/assets/icon/icon.png")))


def _main():
    config.load_configs_from_disk()

    # create config.json on game start if it's been deleted
    if not config.get_config_path().exists():
        config.save_configs_to_disk()

    pygame.init()
    levelbuilder3d.load_player_art()
    create_or_recreate_window()
    highscores.load_score()

    loop = GameLoop()
    loop.start()


if __name__ == "__main__":
    _main()
