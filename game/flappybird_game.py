import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import argparse
from typing import Dict

from game.pygame_base import PygameBase

import pygame, random

from utils.config import Config
from utils.dict_utils import get_with_warning
from game.flappybird.settings import get_settings

game_path = './game/flappybird/'

# pygame.mixer.pre_init(frequency = 44100, size = 16, channels = 1, buffer = 512)
# pygame.init()



config = Config()
    
    
    
class FlappyBirdGame(PygameBase):
    def __init__(
            self, 
            output_dir, 
        ):
        super(FlappyBirdGame, self).__init__(output_dir, "Flappy Bird")
        
        self.screen = pygame.display.set_mode((576,1024))
        self.game_font = pygame.font.Font(os.path.join(game_path, '04B_19.ttf'), 40)
        
        self.bg_surface = pygame.image.load(game_path + 'assets/background-day.png').convert()
        self.bg_surface = pygame.transform.scale2x(self.bg_surface)

        self.floor_surface = pygame.image.load(game_path + 'assets/base.png').convert()
        self.floor_surface = pygame.transform.scale2x(self.floor_surface)

        self.bird_downflap = pygame.transform.scale2x(pygame.image.load(game_path + 'assets/bluebird-downflap.png').convert_alpha())
        self.bird_midflap = pygame.transform.scale2x(pygame.image.load(game_path + 'assets/bluebird-midflap.png').convert_alpha())
        self.bird_upflap = pygame.transform.scale2x(pygame.image.load(game_path + 'assets/bluebird-upflap.png').convert_alpha())
        self.bird_frames = [self.bird_downflap,self.bird_midflap,self.bird_upflap]
        self.bird_index = 0
        self.bird_surface = self.bird_frames[self.bird_index]
        
        bird_center = (100,512)
        self.bird_rect = self.bird_surface.get_rect(center = bird_center)
        
        self.floor_x_pos = 0
        
        self.pipe_surface = pygame.image.load(game_path + 'assets/pipe-green.png')
        self.pipe_surface = pygame.transform.scale2x(self.pipe_surface)

        self.pipe_list = []
        self.bird_movement = 0
        self.create_pipe_count = 100
        self.bird_flip_count = 0      
        
        
    def draw_floor(self):
        self.screen.blit(self.floor_surface,(self.floor_x_pos,900))
        self.screen.blit(self.floor_surface,(self.floor_x_pos + 576,900))

    def set_level_config(self, level_config: Dict):
        self.current_level = self.level_config.get("level", 1)
        
        self.settings = get_settings(self.current_level)
        self.jump_height = get_with_warning(self.settings, "jump_height", 7)
        self.gravity = get_with_warning(self.settings, "gravity", 0.25)
        self.move_speed = get_with_warning(self.settings, "move_speed", 5)
        self.pipe_gap = get_with_warning(self.settings, "pipe_gap", 500)
        self.pipe_frequency = get_with_warning(self.settings, "pipe_frequency", 100)
        self.rotate = get_with_warning(self.settings, "rotate", True)
        self.valid_actions = get_with_warning(self.settings, "valid_actions", ["UP", "KEEP"])
        self.sample_frames = get_with_warning(self.settings, "sample_frame", 3)
    
    def create_pipe(self):
        
        if not self.pipe_list:
            random_pipe_pos = random.randint(self.pipe_gap + 50, 850)
        else:
            # 获取上一个管道的位置
            last_pipe_pos = self.pipe_list[-2]['rect'].midtop[1]
            # 确保新管道与上一个管道的差距不会太大
            min_pipe_pos = max(self.pipe_gap + 50, last_pipe_pos - 300)
            max_pipe_pos = min(850, last_pipe_pos + 300)
            random_pipe_pos = random.randint(min_pipe_pos, max_pipe_pos)
        
        bottom_pipe = {'rect': self.pipe_surface.get_rect(midtop=(700, random_pipe_pos)), 'counted': False}
        top_pipe = {'rect': self.pipe_surface.get_rect(midbottom=(700, random_pipe_pos - self.pipe_gap)), 'counted': False}
        return bottom_pipe, top_pipe

    def move_pipes(self, pipes):
        for pipe in pipes:
            pipe['rect'].centerx -= self.move_speed
        return pipes

    def draw_pipes(self, pipes):
        for idx, pipe in enumerate(pipes):
            if idx % 2 == 0:
                self.screen.blit(self.pipe_surface, pipe['rect'])
            else:
                flip_pipe = pygame.transform.flip(self.pipe_surface, False, True)
                self.screen.blit(flip_pipe, pipe['rect'])
                
    def remove_pipes(self, pipes):
        while pipes[0]['rect'].centerx <= -600:
            pipes.pop(0)
            pipes.pop(0)
        return pipes
    
    def check_collision(self, pipes):
        for pipe in pipes:
            if self.bird_rect.colliderect(pipe['rect']):
                return False

        if self.bird_rect.top <= -100 or self.bird_rect.bottom >= 900:
            return False

        return True

    def rotate_bird(self, bird, movement):
        # new_bird = pygame.transform.rotozoom(bird,-self.bird_movement * 3,1)
        new_bird = pygame.transform.rotozoom(bird,-movement * 3,1)
        return new_bird

    def bird_animation(self):
        new_bird = self.bird_frames[self.bird_index]
        new_bird_rect = new_bird.get_rect(center = (100, self.bird_rect.centery))
        return new_bird,new_bird_rect

    def score_display(self, game_state):
        if game_state == 'main_game':
            score_surface = self.game_font.render(str(int(self.score)),True,(255,255,255))
            score_rect = score_surface.get_rect(center = (288,100))
            self.screen.blit(score_surface,score_rect)

    def get_score(self):
        return {
            "score" : self.score,  # win or lose
            "frames" : len(self.game_frames),
            "valid rate" : len(self.game_frames) / ( len(self.game_frames) + self.invalid_action_count ),
        }
           
    def step(self, action, dt=None):
        self.screen.blit(self.bg_surface,(0,0))
        if action == "UP":
            self.bird_movement = -self.jump_height
        elif action == "DOWN":
            self.bird_movement = self.jump_height
        elif action == "KEEP":
            self.bird_movement = 0
            
            
        self.create_pipe_count += 1
        if self.create_pipe_count >= self.pipe_frequency:
            self.create_pipe_count = 0
            pipe_pair = self.create_pipe()
            self.pipe_list.extend(pipe_pair)
            
        self.bird_flip_count += 1
        if self.bird_flip_count >= 6:
            self.bird_flip_count = 0
            if self.bird_index < 2:
                self.bird_index += 1
            else:
                self.bird_index = 0
            self.bird_surface, self.bird_rect = self.bird_animation()
            
		# Bird
        if self.rotate:
            rotated_bird = self.rotate_bird(self.bird_surface, self.bird_movement)
        else:
            rotated_bird = self.rotate_bird(self.bird_surface, 0)
            
        self.bird_rect.centery += self.bird_movement
        self.screen.blit(rotated_bird, self.bird_rect)
        game_active = self.check_collision(self.pipe_list)
        if not game_active:
            self.over = True
            return True, "Game over!"

        if self.gravity == 0:
            self.bird_movement = 0
        else:
            self.bird_movement += self.gravity
            
        # Pipes
        self.pipe_list = self.move_pipes(self.pipe_list)
        self.pipe_list = self.remove_pipes(self.pipe_list)
        self.draw_pipes(self.pipe_list)
		
  
        for pipe in self.pipe_list:
            if pipe['rect'].centerx <= 100 and not pipe['counted']:
                self.score += 0.5
                pipe['counted'] = True
        
        self.score_display('main_game')
        
        
        # screen.blit(game_over_surface,game_over_rect)
        # high_score = update_score(score,high_score)
        # score_display('game_over')
        
        # Floor
        self.floor_x_pos -= 1
        self.draw_floor()
        if self.floor_x_pos <= -576:
            self.floor_x_pos = 0
            
        pygame.display.update()
        
        return False, "Game continues."
        
    def human_mode_action(self, event):
        action = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                action = "UP"
            elif event.key == pygame.K_DOWN:
                action = "DOWN"
            elif event.key == pygame.K_LCTRL:
                action = "KEEP"
            elif event.key == pygame.K_LEFT:
                action = "NONE"
        return action
    
    

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument("--levelConfig", type=str, default="./config/level_config/flappybirdgame/level1.json", help="The path to the level config file.")
    parser.add_argument("--level", type=int, default=1, help="The level of the game.")
    args = parser.parse_args()
    
    level = args.level
    
    levelConfig = f"./config/level_config/flappybirdgame/level{level}.json"
    
    config.load_level_config(levelConfig)
    
    flappybird_game = FlappyBirdGame("")
    
    flappybird_game.run(None, human_mode=True)
    
    
# python game/flappybird_game.py --level 4
    