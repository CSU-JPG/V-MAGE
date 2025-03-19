import argparse
import random
import pygame, sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")


from game.Pong.settings import get_settings
from utils.dict_utils import get_with_warning
from game.pygame_base import PygameBase
from utils.config import Config

config = Config()

class PongGame(PygameBase):
    def __init__(
            self,
            output_dir,
    ):
        super(PongGame, self).__init__(output_dir, "Pong Game")
    
        self.font = pygame.font.SysFont('Courier', self.font_size)
    
        self.max_round = -1 # inf
        
        self.valid_actions = ["LEFTUP", "LEFTDOWN", "RIGHTUP", "RIGHTDOWN", "NONE"]   
        
        self.sample_frames = 3
    
    def set_level_config(self, level_config):
        self.current_level = level_config.get("level", 0)
        
        setting = get_settings(self.current_level)
        self.width, self.height = 800, 600
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)

        self.paddle_width, self.paddle_height = get_with_warning(setting, "paddle", (10, 150))
        self.ball_size = get_with_warning(setting, "ball_size", 40)
        self.paddle_speed = get_with_warning(setting, "paddle_speed", 10)
        self.ball_speed = get_with_warning(setting, "ball_speed", 40)
        self.font_size = get_with_warning(setting, "font_size", 30)
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # 分数
        self.scoreA = 0
        self.scoreB = 0

        # 创建球
        self.ball = pygame.Rect(self.width // 2 - self.ball_size // 2, self.height // 2 - self.ball_size // 2, self.ball_size, self.ball_size)
        left_or_right = random.choice([-1, 1])
        self.ball_dx = left_or_right * self.ball_speed
        # random choose continuse speed
        up_or_down = random.uniform(-1, 1)
        self.ball_dy = up_or_down * self.ball_speed

        # 创建球拍
        self.paddleA = pygame.Rect(20, self.height // 2 - self.paddle_height // 2, self.paddle_width, self.paddle_height)
        self.paddleB = pygame.Rect(self.width - 20 - self.paddle_width, self.height // 2 - self.paddle_height // 2, self.paddle_width, self.paddle_height)

        # 边界线
        self.border_up = self.height // 2 - 15
        self.border_down = -self.height // 2 + 15
        self.border_left = self.width // 2 - 20
        self.border_right = -self.width // 2 + 20
    
    def draw_field(self):
        # 绘制边框
        pygame.draw.rect(self.screen, self.white, pygame.Rect(10, 10, self.width - 20, self.height - 20), 2)
        # 中线
        pygame.draw.aaline(self.screen, self.white, (self.width // 2, 10), (self.width // 2, self.height - 10))

    def draw_objects(self):
        # 绘制球拍和球
        pygame.draw.rect(self.screen, self.white, self.paddleA)
        pygame.draw.rect(self.screen, self.white, self.paddleB)
        pygame.draw.ellipse(self.screen, self.white, self.ball)

    def draw_score(self):
        score_text = self.font.render(f"Player A: {self.scoreA}    Player B: {self.scoreB}", True, self.white)
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 40))

    def handle_movement(self, keys):
        # 控制 Paddle A
        if keys[pygame.K_w] and self.paddleA.top > 10:
            self.paddleA.y -= self.paddle_speed
        if keys[pygame.K_s] and self.paddleA.bottom < self.height - 10:
            self.paddleA.y += self.paddle_speed
        # 控制 Paddle B
        if keys[pygame.K_UP] and self.paddleB.top > 10:
            self.paddleB.y -= self.paddle_speed
        if keys[pygame.K_DOWN] and self.paddleB.bottom < self.height - 10:
            self.paddleB.y += self.paddle_speed

    def move_ball(self):
        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        # 上下边界碰撞
        if self.ball.top <= 10 or self.ball.bottom >= self.height - 10:
            self.ball_dy *= -1


        def change_y_speed():
            random_ddy = 0.5 * random.uniform(-self.ball_speed, self.ball_speed)
            self.ball_dy = self.ball_dy + random_ddy
            self.ball_dy = min(self.ball_speed, self.ball_dy)
            self.ball_dy = max(-self.ball_speed, self.ball_dy)
        
        # 球与球拍碰撞        
        if self.paddleA.top <= self.ball.y <= self.paddleA.bottom and self.ball_dx < 0 and self.ball.x <= self.paddleA.right:
            self.ball.x = self.paddleA.right
            self.scoreA += 1
            self.ball_dx *= -1
            change_y_speed()
            
        if self.paddleB.top <= self.ball.y <= self.paddleB.bottom and self.ball_dx > 0 and self.ball.x + self.ball_size >= self.paddleB.left:
            self.ball.x = self.paddleB.left - self.ball_size
            self.scoreB += 1
            self.ball_dx *= -1
            change_y_speed()
            
        
        # 左右边界得分
        if self.ball.x <= self.paddleA.x - 10:
            # self.reset_ball()
            self.over = True
        if self.ball.x >= self.paddleB.x + 10:
            # self.reset_ball()
            self.over = True

    def reset_ball(self):
        self.ball.center = (self.width // 2, self.height // 2)
        
        self.ball_dx *= -1
        
    def step(self, action, dt=None):
        if action == "LEFTUP" and self.paddleA.top > 10:
            self.paddleA.y -= self.paddle_speed
        elif action == "LEFTDOWN" and self.paddleA.bottom < self.height - 10:
            self.paddleA.y += self.paddle_speed
        elif action == "RIGHTUP" and self.paddleB.top > 10:
            self.paddleB.y -= self.paddle_speed 
        elif action == "RIGHTDOWN" and self.paddleB.bottom < self.height - 10:
            self.paddleB.y += self.paddle_speed
        
        self.move_ball()

        # 绘制
        self.screen.fill(self.black)
        self.draw_field()
        self.draw_objects()
        self.draw_score()
        pygame.display.flip()
        
        self.score = self.scoreA + self.scoreB
        
        if self.over:
            return True, f"Game Over, You got {self.score} score."
        else:
            return False, "Game is running."
        
        
    
        
    def human_mode_action(self, event):
        action = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                action = "RIGHTUP"
            elif event.key == pygame.K_DOWN:
                action = "RIGHTDOWN"
            elif event.key == pygame.K_w:
                action = "LEFTUP"
            elif event.key == pygame.K_s:
                action = "LEFTDOWN"
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
    parser.add_argument("--levelConfig", type=str, default="./config/level_config/ponggame/level2.json", help="The path to the level config file.")
    args = parser.parse_args()
    
    levelConfig = args.levelConfig
    
    config.load_level_config(levelConfig)
    
    pong_game = PongGame("")
    
    pong_game.run(None, human_mode=True)
    
# python game/pong_game.py 