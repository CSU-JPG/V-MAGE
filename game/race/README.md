![Alt text](images/main_menu_image.png?raw=true)
##YouTube DEMO Video
https://youtu.be/A8tv_3M1tR4

## Overview: This car racing game is my first python project and was a fun way to learn Python and get experience with Pygame. The game is reminiscent of most 2d racing games, there is a starting point and an ending point, in this case a trophy. Contact with the trophy in the allotted time will satisfy the win condition and allow you to proceed, collision with any of the wall barriers or an expiration of the timer will fail you. There are 3 levels in total, of increasing difficulty. Good luck! If you cannot play this game for whatever reason, I have attached a video showing the gameplay at the bottom of the README.


##How To Play: Make sure you have a copy of Python 2.7 installed and the Pygame library. Open the Main_menu.py to begin and follow the prompt to continue. Good Luck!

#Example terminal command:
```
python Main_Menu.py
```
##Controls:
- Up Arrow: Acceleration
- Down Arrow: Brake, Reverse
- Left/Right Arrows: Turn
- Escape: Exit
- Space: Continue/Retry (at level end)

##Languages used: 
  - Python
  
  Library:
  - Pygame

  Design:
  - Paintbrush

##MVP (Minimum Viable Product): 
Initial MVP
  - One, bug-free, complete level from start to finish
  
Strech Goals
  - Multiple levels
  - Timed condition
  - Multiple lives
  - Multiplayer support
  

##Code Snippets
This is the code from the first level, the second and third levels are essentially the same with tweaks to barrier placement and timer settings.
``` python
#initialize the screen
import pygame, math, sys, level2, time
from pygame.locals import *

def level1():
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    #GAME CLOCK
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 75)
    win_font = pygame.font.Font(None, 50)
    win_condition = None
    win_text = font.render('', True, (0, 255, 0))
    loss_text = font.render('', True, (255, 0, 0))
    t0 = time.time()
    



    class CarSprite(pygame.sprite.Sprite):
        MAX_FORWARD_SPEED = 10
        MAX_REVERSE_SPEED = 10
        ACCELERATION = 2
        TURN_SPEED = 10

        def __init__(self, image, position):
            pygame.sprite.Sprite.__init__(self)
            self.src_image = pygame.image.load(image)
            self.position = position
            self.speed = self.direction = 0
            self.k_left = self.k_right = self.k_down = self.k_up = 0
        
        def update(self, deltat):
            #SIMULATION
            self.speed += (self.k_up + self.k_down)
            if self.speed > self.MAX_FORWARD_SPEED:
                self.speed = self.MAX_FORWARD_SPEED
            if self.speed < -self.MAX_REVERSE_SPEED:
                self.speed = -self.MAX_REVERSE_SPEED
            self.direction += (self.k_right + self.k_left)
            x, y = (self.position)
            rad = self.direction * math.pi / 180
            x += -self.speed*math.sin(rad)
            y += -self.speed*math.cos(rad)
            self.position = (x, y)
            self.image = pygame.transform.rotate(self.src_image, self.direction)
            self.rect = self.image.get_rect()
            self.rect.center = self.position

    class PadSprite(pygame.sprite.Sprite):
        normal = pygame.image.load('images/race_pads.png')
        hit = pygame.image.load('images/collision.png')
        def __init__(self, position):
            super(PadSprite, self).__init__()
            self.rect = pygame.Rect(self.normal.get_rect())
            self.rect.center = position
        def update(self, hit_list):
            if self in hit_list: self.image = self.hit
            else: self.image = self.normal
    pads = [
        PadSprite((0, 10)),
        PadSprite((600, 10)),
        PadSprite((1100, 10)),
        PadSprite((100, 150)),
        PadSprite((600, 150)),
        PadSprite((100, 300)),
        PadSprite((800, 300)),
        PadSprite((400, 450)),
        PadSprite((700, 450)),
        PadSprite((200, 600)),
        PadSprite((900, 600)),
        PadSprite((400, 750)),
        PadSprite((800, 750)),
    ]
    pad_group = pygame.sprite.RenderPlain(*pads)

    class Trophy(pygame.sprite.Sprite):
        def __init__(self, position):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load('images/trophy.png')
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = position
        def draw(self, screen):
            screen.blit(self.image, self.rect)

    trophy = [Trophy((285,0))]
    trophy_group = pygame.sprite.RenderPlain(*trophy)

    # CREATE A CAR AND RUN
    rect = screen.get_rect()
    car = CarSprite('images/car.png', (10, 730))
    car_group = pygame.sprite.RenderPlain(car)

    #THE GAME LOOP
    while 1:
        #USER INPUT
        t1 = time.time()
        dt = t1-t0

        deltat = clock.tick(30)
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            down = event.type == KEYDOWN 
            if win_condition == None: 
                if event.key == K_RIGHT: car.k_right = down * -5 
                elif event.key == K_LEFT: car.k_left = down * 5
                elif event.key == K_UP: car.k_up = down * 2
                elif event.key == K_DOWN: car.k_down = down * -2 
                elif event.key == K_ESCAPE: sys.exit(0) # quit the game
            elif win_condition == True and event.key == K_SPACE: level2.level2()
            elif win_condition == False and event.key == K_SPACE: 
                level1()
                t0 = t1
            elif event.key == K_ESCAPE: sys.exit(0)    
    
        #COUNTDOWN TIMER
        seconds = round((20 - dt),2)
        if win_condition == None:
            timer_text = font.render(str(seconds), True, (255,255,0))
            if seconds <= 0:
                win_condition = False
                timer_text = font.render("Time!", True, (255,0,0))
                loss_text = win_font.render('Press Space to Retry', True, (255,0,0))
            
    
        #RENDERING
        screen.fill((0,0,0))
        car_group.update(deltat)
        collisions = pygame.sprite.groupcollide(car_group, pad_group, False, False, collided = None)
        if collisions != {}:
            win_condition = False
            timer_text = font.render("Crash!", True, (255,0,0))
            car.image = pygame.image.load('images/collision.png')
            loss_text = win_font.render('Press Space to Retry', True, (255,0,0))
            seconds = 0
            car.MAX_FORWARD_SPEED = 0
            car.MAX_REVERSE_SPEED = 0
            car.k_right = 0
            car.k_left = 0

        trophy_collision = pygame.sprite.groupcollide(car_group, trophy_group, False, True)
        if trophy_collision != {}:
            seconds = seconds
            timer_text = font.render("Finished!", True, (0,255,0))
            win_condition = True
            car.MAX_FORWARD_SPEED = 0
            car.MAX_REVERSE_SPEED = 0
            win_text = win_font.render('Press Space to Advance', True, (0,255,0))
            if win_condition == True:
                car.k_right = -5
                
        pad_group.update(collisions)
        pad_group.draw(screen)
        car_group.draw(screen)
        trophy_group.draw(screen)
        #Counter Render
        screen.blit(timer_text, (20,60))
        screen.blit(win_text, (250, 700))
        screen.blit(loss_text, (250, 700))
        pygame.display.flip()


```
##Screenshots
![Alt text](images/level1_screenshot.png?raw=true)
Level 1

![Alt text](images/crash_screenshot.png?raw=true)
Crash Screenshot

  
##Project History
Start: 06/27/17
End: 07/30/17
8/1/30 added title screen and README
