import argparse
import pygame, sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")


from utils.dict_utils import get_with_warning
from game.pygame_base import PygameBase
from utils.config import Config
from game.supermario.classes.Dashboard import Dashboard
from game.supermario.classes.Level import Level
from game.supermario.classes.Menu import Menu
from game.supermario.classes.Sound import Sound
from game.supermario.entities.Mario import Mario

config = Config()


class SuperMarioGame(PygameBase):
    def __init__(
            self,
            output_dir,
    ):
        super(SuperMarioGame, self).__init__(output_dir, "Super Mario")
        
        self.valid_actions = ["UP", "LEFT", "RIGHT", "UP+LEFT", "UP+RIGHT", "NONE"]   
        
        self.sample_frames = 5 
    
    def set_level_config(self, level_config):
        current_level = get_with_warning(level_config, "level", 0)
        self.max_round = get_with_warning(level_config, "max_round", 300)
        
        windowSize = 640, 480
        self.screen = pygame.display.set_mode(windowSize)
        
        self.dashboard = Dashboard("game/supermario/img/font.png", 8, self.screen)
        self.sound = Sound()
        self.level = Level(self.screen, self.sound, self.dashboard)
        self.menu = Menu(self.screen, self.dashboard, self.level, self.sound)
        
        self.menu.levelNames = self.menu.loadLevelNames()
        self.menu.inChoosingLevel = False
        self.menu.dashboard.state = "start"
        self.menu.dashboard.time = 0
        self.menu.level.loadLevel(self.menu.levelNames[current_level])
        
        
        self.menu.dashboard.levelName = self.menu.levelNames[current_level].split("Level")[1]
        self.menu.start = True
        
        self.mario = Mario(0, 0, self.level, self.screen, self.dashboard, self.sound)
        
    def step(self, action, dt=None):
        self.level.drawLevel(self.mario.camera)
        self.dashboard.update()
        self.mario.update(action)
        pygame.display.update()
        if len(self.game_frames) >= self.max_round or self.mario.restart:
            self.over = True
        
        self.score = self.dashboard.points
        if self.over:
            info = f"Game Over, You got {self.score} scores."    
        else:
            info = "Game is running."
        return self.over, info
    
        
    def human_mode_action(self, event):
        action = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                action = "UP"
            elif event.key == pygame.K_DOWN:
                action = "DOWN"
            elif event.key == pygame.K_LEFT:
                action = "LEFT"
            elif event.key == pygame.K_RIGHT:
                action = "RIGHT"
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
    parser.add_argument("--levelConfig", type=str, default="./config/level_config/supermariogame/level1.json", help="The path to the level config file.")
    args = parser.parse_args()
    
    levelConfig = args.levelConfig
    
    config.load_level_config(levelConfig)
    
    supermario_game = SuperMarioGame("")
    
    supermario_game.run(None, human_mode=True)
    
# python game/supermario_game.py 