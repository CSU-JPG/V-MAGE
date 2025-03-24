import argparse
import pygame, sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")


from utils.dict_utils import get_with_warning
from game.pygame_base import PygameBase
from utils.config import Config


import game.tempestrun.rendering.levelbuilder3d as levelbuilder3d
import game.tempestrun.gameplay.gamestuff as gamestuff



config = Config()


class TempestRunGame(PygameBase):
    def __init__(
            self,
            output_dir,
    ):
        super(TempestRunGame, self).__init__(output_dir, "Tempest Run")
        
        self.current_mode.on_mode_start()
        
        self.valid_actions = ["JUMP", "LEFT", "RIGHT", "SLIDE", "RISE", "NONE"]   
        
        self.sample_frames = 3
        
        self.action_in_sample_frames = "NONE"
    
    def set_level_config(self, level_config):
        
        windowSize = 1024, 768
        pygame.display.set_mode(windowSize)
        self.screen = pygame.display.get_surface()
        
        
        current_level = level_config.get("level", 1)
        self.current_mode = gamestuff.GameplayMode(self, current_level)
        
        
        
    def step(self, action, dt=None):
        
        events = []
        
        if action == "JUMP":
            events.append(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP}))
        elif action == "SLIDE":
            events.append(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_DOWN}))
        elif action == "LEFT":
            events.append(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT}))
        elif action == "RIGHT":
            events.append(pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RIGHT}))
        elif action == "RISE":
            events.append(pygame.event.Event(pygame.KEYUP, {"key": pygame.K_DOWN}))
            
        
        cur_mode = self.current_mode

        cur_mode.update(dt, events)
        cur_mode.draw_to_screen(self.screen)

        pygame.display.flip()
        
        if self.current_mode.player.is_dead():
            self.running = False
            self.over = True
        
        self.score = self.current_mode.player.get_score()
        if self.over:
            info = f"Game Over, You got {self.score} scores."    
        else:
            info = "Game is running."
        return self.over, info
    
        
    def human_mode_action(self, event):
        action = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                action = "JUMP"
            elif event.key == pygame.K_DOWN:
                action = "SLIDE"
            elif event.key == pygame.K_LEFT:
                action = "LEFT"
            elif event.key == pygame.K_RIGHT:
                action = "RIGHT"
            elif event.key == pygame.K_SPACE:
                action = "RISE"
            else:
                action = "NONE"
        return action

    def get_score(self):
        return {
            "score" : self.score,  # win or lose
            "frames" : len(self.game_frames),
            "valid rate" : len(self.game_frames) / ( len(self.game_frames) + self.invalid_action_count ),
        }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--levelConfig", type=str, default="./config/level_config/tempestrungame/level4.json", help="The path to the level config file.")
    args = parser.parse_args()
    
    levelConfig = args.levelConfig
    
    config.load_level_config(levelConfig)
    
    tempestrun_game = TempestRunGame("")
    
    tempestrun_game.run(None, human_mode=True)
    
# python game/tempestrun_game.py 