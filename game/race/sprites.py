import pygame, math

from game.race.utils import pygame_image_scale
from utils.dict_utils import get_with_warning


class CarSprite(pygame.sprite.Sprite):
    ACCELERATION = 2
    TURN_SPEED = 10

    def __init__(self, **kargs):
        pygame.sprite.Sprite.__init__(self)
        
        assert 'car_position' in kargs, 'car_position is required'
        self.position = get_with_warning(kargs, 'car_position', (100, 100))
        
        self.direction = get_with_warning(kargs, 'direction', 0)
        self.speed = get_with_warning(kargs, 'init_speed', 0)
        self.speed_attenuation = get_with_warning(kargs, 'speed_attenuation', 0.98)
        self.MAX_FORWARD_SPEED = get_with_warning(kargs, 'MAX_FORWARD_SPEED', 10)
        self.MAX_REVERSE_SPEED = get_with_warning(kargs, 'MAX_REVERSE_SPEED', 10)
        self.ACCELERATION = get_with_warning(kargs, 'ACCELERATION', 2)
        self.TURN_SPEED = get_with_warning(kargs, 'TURN_SPEED', 10)
        
        self.car_image = get_with_warning(kargs, 'car_image', './game/race/images/white_car.png')
        self.car_image_scale = get_with_warning(kargs, 'car_image_scale', 0.2)
        self.src_image = pygame_image_scale(pygame.image.load(self.car_image), self.car_image_scale)
        self.clear_k()
        
        self.rect = self.src_image.get_rect(center=self.position)
    
        self.viewpoint = get_with_warning(kargs, "viewpoint", "car")
        
        
    def clear_k(self):
        self.k_left = self.k_right = self.k_down = self.k_up = 0
        
    def update(self, action):
        #SIMULATION
        
        if self.viewpoint == "car":
            if action == "RIGHT":
                self.k_right = -self.TURN_SPEED
            elif action == "LEFT":
                self.k_left = self.TURN_SPEED
            elif action == "FORWARD":
                self.k_up = self.ACCELERATION
            elif action == "BACKWARD":
                self.k_down = -self.ACCELERATION
                
            self.speed += (self.k_up + self.k_down)
            if self.speed > self.MAX_FORWARD_SPEED:
                self.speed = self.MAX_FORWARD_SPEED
            elif self.speed < -self.MAX_REVERSE_SPEED:
                self.speed = -self.MAX_REVERSE_SPEED
            else:
                self.speed = self.speed * self.speed_attenuation
            if self.speed >= 0:
                self.direction += (self.k_right + self.k_left)
            else:
                self.direction -= (self.k_right + self.k_left)
                
            self.direction = (self.direction % 360 + 359) % 360 + 1
            x, y = (self.position)
            rad = self.direction * math.pi / 180
            x += -self.speed*math.sin(rad)
            y += -self.speed*math.cos(rad)
            self.position = (x, y)
            self.image = pygame.transform.rotate(self.src_image, self.direction)
            # self.rect = self.image.get_rect()
            self.rect = self.image.get_rect(center=self.rect.center)
            self.rect.center = self.position

        elif self.viewpoint == "map":
            x, y = (self.position)
            if action == "RIGHT":
                x += self.ACCELERATION
            elif action == "LEFT":
                x -= self.ACCELERATION
            elif action == "UP":
                y -= self.ACCELERATION
            elif action == "DOWN":
                y += self.ACCELERATION
            self.position = (x, y)
            self.image = self.src_image
            self.rect.center = self.position
            # self.image is no need to update
            
            
        # DEBUG
        
        # Draw a border around the rectangle
        # border_color = (255, 0, 0)  # 边框颜色，红色
        # border_width = 2           # 边框宽度
        # # 创建一个新的表面
        # bordered_image = pygame.Surface((self.rect.width + 2 * border_width, 
        #                                 self.rect.height + 2 * border_width), pygame.SRCALPHA)
        # bordered_image.fill((0, 0, 0, 0))  # 设置为透明背景
        # # 在表面上绘制边框
        # pygame.draw.rect(bordered_image, border_color, 
        #                 (0, 0, bordered_image.get_width(), bordered_image.get_height()), border_width)
        # # 将旋转后的图像绘制到边框中心
        # bordered_image.blit(self.image, (border_width, border_width))
        # self.image = bordered_image

class SquarePadSprite(pygame.sprite.Sprite):
    normal = pygame.image.load('./game/race/images/square.png')
    def __init__(self, position):
        super(SquarePadSprite, self).__init__()
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image = self.normal

class VertivalPadSprite(pygame.sprite.Sprite):
    normal = pygame.image.load('./game/race/images/vertical_pads.png')
    def __init__(self, position):
        super(VertivalPadSprite, self).__init__()
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image = self.normal
        
class RacePadSprite(pygame.sprite.Sprite):
    normal = pygame.image.load('./game/race/images/race_pads.png')
    hit = pygame.image.load('./game/race/images/collision.png')
    def __init__(self, position):
        super(RacePadSprite, self).__init__()
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image = self.normal

class HorizontalPad(pygame.sprite.Sprite):
    normal = pygame.image.load('./game/race/images/race_pads.png')
    def __init__(self, position):
        super(HorizontalPad, self).__init__()
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image = self.normal

class SmallHorizontalPad(pygame.sprite.Sprite):
    normal = pygame.image.load('./game/race/images/small_horizontal.png')
    def __init__(self, position):
        super(SmallHorizontalPad, self).__init__()
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image = self.normal

class SmallVerticalPad(pygame.sprite.Sprite):
    normal = pygame.image.load('./game/race/images/small_vertical.png')
    def __init__(self, position):
        super(SmallVerticalPad, self).__init__()
        self.rect = pygame.Rect(self.normal.get_rect())
        self.rect.center = position
        self.image = self.normal      

class Trophy(pygame.sprite.Sprite):
    def __init__(self, position, trophy_image_scale=1.8):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame_image_scale(pygame.image.load('./game/race/images/trophy.png'), trophy_image_scale)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = position
    def draw(self, screen):
        screen.blit(self.image, self.rect)