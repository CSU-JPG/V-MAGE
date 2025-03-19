import argparse
from typing import Dict
import pygame, sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from game.race.utils import get_distance
from utils.config import Config
from utils.game_utils import capture

import pygame
from game.race.settings import get_settings
from game.race.sprites import *
from pygame.locals import *
from game.pygame_base import PygameBase

config = Config()



class RaceGame(PygameBase):
    def __init__(
            self, 
            output_dir, 
        ):
        super(RaceGame, self).__init__(output_dir, "RaceGame")
        
        self.font = pygame.font.Font(None, 75)
        self.small_font = pygame.font.Font(None, 40)
        self.win_font = pygame.font.Font(None, 50)
        self.win_condition = None
        self.win_text = self.font.render('', True, (0, 255, 0))
        self.loss_text = self.font.render('', True, (255, 0, 0))
        self.speed_text = self.font.render('', True, (0, 255, 0))
        self.angle_text = self.font.render('', True, (0, 255, 0))
    
    def set_level_config(self, level_config: Dict):
        self.screen_size = level_config.get("screen_size", (1024, 768))
        
        
        self.current_level = level_config.get("level", 1)
        self.dynamic = level_config.get("dynamic", "False") == "True"
        
        self.settings = get_settings(self.current_level, self.dynamic)
        
        self.sample_frames = get_with_warning(self.settings, "sample_frame", 1)
        self.maximum_time = get_with_warning(self.settings, "maximum_time", 20)
        self.trophy_image_scale = get_with_warning(self.settings, "trophy_image_scale", 1.8)
        
        assert "pads" in self.settings, "The pads should be defined in the level config."
        self.pads = self.settings["pads"]
        assert "trophy_position" in self.settings, "The trophy_position should be defined in the level config."
        self.trophy_position = self.settings["trophy_position"]
        
        self.valid_actions = get_with_warning(self.settings, "valid_actions", ["FORWARD", "BACKWARD", "LEFT", "RIGHT"])
        
        # 
        self.screen = pygame.display.set_mode(self.screen_size)
        self.pad_group = pygame.sprite.RenderPlain(*self.pads)
        
        self.trophy = Trophy(self.trophy_position, self.trophy_image_scale)
        self.trophy_group = pygame.sprite.RenderPlain(self.trophy)

        # CREATE A CAR AND RUN
        # self.car = CarSprite(position=self.car_position, direction=self.direction, )
        self.car = CarSprite(**self.settings)
        self.car_group = pygame.sprite.RenderPlain(self.car)

        # self.remaining_time = self.maximum_time
        
        self.time_test = False
        
        self.show_speed_text = get_with_warning(self.settings, "speed_text", False)
        self.show_angle_text = get_with_warning(self.settings, "angle_text", False)
        
        self.max_rounds = get_with_warning(self.settings, "max_rounds", 100)
        
        self.origin_distance = get_distance(self.car, self.trophy)
        self.invalid_action_count = 0
    
    def __repr__(self) -> str:
        return "Can not be representation in string." + f" Score: {self.score}\n" 
    def __str__(self) -> str:
        return self.__repr__()
    
    def render(self):
        #RENDERING
        self.screen.fill((0,0,0))
        
        collisions = pygame.sprite.groupcollide(self.car_group, self.pad_group, False, False, collided = None)
        if collisions != {}:
            self.over = True
            self.win_condition = False
            self.timer_text = self.font.render("Crash!", True, (255,0,0))
            self.car.image = pygame.image.load('./game/race/images/collision.png')
            self.loss_text = self.win_font.render('Press Space to Retry', True, (255,0,0))
            self.car.MAX_FORWARD_SPEED = 0
            self.car.MAX_REVERSE_SPEED = 0
            self.car.k_right = 0
            self.car.k_left = 0

        trophy_collision = pygame.sprite.groupcollide(self.car_group, self.trophy_group, False, True)
        if trophy_collision != {}:
            self.over = True
            self.win_condition = True
            self.timer_text = self.font.render("Finished!", True, (0,255,0))
            # TODO
            self.score = 100
            self.car.MAX_FORWARD_SPEED = 0
            self.car.MAX_REVERSE_SPEED = 0
            self.win_text = self.win_font.render('Press Space to Advance', True, (0,255,0))
        
                   
        self.speed_text = self.small_font.render(f"Speed: {round(self.car.speed, 2)}", True, (0,255,0)) 
        self.angle_text = self.small_font.render(f"Direction: {360 - self.car.direction}°", True, (0,255,0))            
        
        self.pad_group.update(collisions)
        self.pad_group.draw(self.screen)
        self.car_group.draw(self.screen)
        self.trophy_group.draw(self.screen)
        
        #Counter Render
        if self.show_speed_text:
            self.screen.blit(self.speed_text, (60,60))
        if self.show_angle_text:
            self.screen.blit(self.angle_text, (60,90))
        if self.time_test:
            self.screen.blit(self.timer_text, (20,60))
        self.screen.blit(self.win_text, (250, 700))
        self.screen.blit(self.loss_text, (250, 700))
        
        pygame.display.flip()

    def get_score(self):
        return {
            "score" : self.score,  # win or lose
            "completion degree" : max(0, self.origin_distance - get_distance(self.car, self.trophy)) / self.origin_distance,
            "frames" : len(self.game_frames),
            "valid rate" : len(self.game_frames) / ( len(self.game_frames) + self.invalid_action_count ),
        }
    
    def step(self, action, dt=None):
        if len(self.game_frames) >= self.max_rounds:
            self.over = True
            self.win_condition = False
            self.timer_text = self.font.render("Max Rounds!", True, (255,0,0))
            self.loss_text = self.win_font.render('Press Retry', True, (255,0,0))
            return self.over, "Game Over, You got 0 score, you failed!"
        self.car.clear_k()

        self.car_group.update(action)  
              
        #COUNTDOWN TIMER
        # if self.time_test:
        #     seconds = round(self.remaining_time, 2)
        #     self.timer_text = self.font.render(str(seconds), True, (255,255,0))
        #     if seconds <= 0:
        #         self.over = True
        #         self.timer_text = self.font.render("Time!", True, (255,0,0))
        #         self.loss_text = self.win_font.render('Press Retry', True, (255,0,0))
        # else:
        #     self.timer_text = self.font.render("", True, (255,255,0))
        
        self.render()
        
        if self.over:
            info = f"Game Over, You got {self.score} score, you {'successed!' if self.win_condition else 'failed!'}"    
        else:
            info = "Game is running."
        return self.over, info
    
    def human_mode_action(self, event):
        action = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                action = "FORWARD" if "FORWARD" in self.valid_actions else "UP"
            elif event.key == pygame.K_DOWN:
                action = "BACKWARD" if "BACKWARD" in self.valid_actions else "DOWN"
            elif event.key == pygame.K_LEFT:
                action = "LEFT"
            elif event.key == pygame.K_RIGHT:
                action = "RIGHT"
            else:
                action = "NONE"
        return action

        

if __name__ == '__main__':   
    parser = argparse.ArgumentParser()
    parser.add_argument("--levelConfig", type=str, default="./config/level_config/racegame/level7.json", help="The path to the level config file.")
    args = parser.parse_args()
    
    levelConfig = args.levelConfig
    
    config.load_level_config(levelConfig)
    
    race_game = RaceGame("")
    
    race_game.run(None, human_mode=True)
    
# python game/race_game.py --levelConfig ./config/level_config/racegame/level4.json