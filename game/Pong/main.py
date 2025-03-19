import pygame
import sys

# 初始化 Pygame
pygame.init()

# 常量定义
WIDTH, HEIGHT = 800, 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 60

PADDLE_WIDTH, PADDLE_HEIGHT = 10, 200
BALL_SIZE = 40
PADDLE_SPEED = 5
BALL_SPEED_X, BALL_SPEED_Y = 4, 4
FONT_SIZE = 30

class PongGame:
    def __init__(self):
        # 设置窗口
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Pong')

        # 创建时钟对象
        self.clock = pygame.time.Clock()

        # 创建字体
        self.font = pygame.font.SysFont('Courier', FONT_SIZE)

        # 分数
        self.scoreA = 0
        self.scoreB = 0

        # 创建球
        self.ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.ball_dx = BALL_SPEED_X
        self.ball_dy = BALL_SPEED_Y

        # 创建球拍
        self.paddleA = pygame.Rect(20, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.paddleB = pygame.Rect(WIDTH - 20 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

        # 边界线
        self.border_up = HEIGHT // 2 - 15
        self.border_down = -HEIGHT // 2 + 15
        self.border_left = WIDTH // 2 - 20
        self.border_right = -WIDTH // 2 + 20

    def draw_field(self):
        # 绘制边框
        pygame.draw.rect(self.screen, WHITE, pygame.Rect(10, 10, WIDTH - 20, HEIGHT - 20), 2)
        # 中线
        pygame.draw.aaline(self.screen, WHITE, (WIDTH // 2, 10), (WIDTH // 2, HEIGHT - 10))

    def draw_objects(self):
        # 绘制球拍和球
        pygame.draw.rect(self.screen, WHITE, self.paddleA)
        pygame.draw.rect(self.screen, WHITE, self.paddleB)
        pygame.draw.ellipse(self.screen, WHITE, self.ball)

    def draw_score(self):
        score_text = self.font.render(f"Player A: {self.scoreA}    Player B: {self.scoreB}", True, WHITE)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

    def handle_movement(self, keys):
        # 控制 Paddle A
        if keys[pygame.K_w] and self.paddleA.top > 10:
            self.paddleA.y -= PADDLE_SPEED
        if keys[pygame.K_s] and self.paddleA.bottom < HEIGHT - 10:
            self.paddleA.y += PADDLE_SPEED
        # 控制 Paddle B
        if keys[pygame.K_UP] and self.paddleB.top > 10:
            self.paddleB.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and self.paddleB.bottom < HEIGHT - 10:
            self.paddleB.y += PADDLE_SPEED

    def move_ball(self):
        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        # 上下边界碰撞
        if self.ball.top <= 10 or self.ball.bottom >= HEIGHT - 10:
            self.ball_dy *= -1

        # 左右边界得分
        if self.ball.left <= 10:
            self.scoreB += 1
            self.reset_ball()
        if self.ball.right >= WIDTH - 10:
            self.scoreA += 1
            self.reset_ball()

        # 球与球拍碰撞
        if self.ball.colliderect(self.paddleA) and self.ball_dx < 0:
            self.ball_dx *= -1
        if self.ball.colliderect(self.paddleB) and self.ball_dx > 0:
            self.ball_dx *= -1

    def reset_ball(self):
        self.ball.center = (WIDTH // 2, HEIGHT // 2)
        self.ball_dx *= -1

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            self.handle_movement(keys)

            self.move_ball()

            # 绘制
            self.screen.fill(BLACK)
            self.draw_field()
            self.draw_objects()
            self.draw_score()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PongGame()
    game.run()
