import base64
from datetime import datetime
import pygame, os
import time

from utils.config import Config

config = Config()

def capture(pygame_screen, output_dir):
    if output_dir == "":
        pygame.image.save(pygame_screen, "tmp.png")
        filepath = "tmp.png"
    else:
        filepath = os.path.join(output_dir, "screen_" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".png")
        # 获取当前屏幕的大小
        
        screen_width, screen_height = pygame_screen.get_size()
        
        if config.resolution_height == -1:
            if config.resolution_width == -1:
                image_size_height = 360
                image_size = (int(screen_width * image_size_height / screen_height), image_size_height)
            else:
                image_size_width = config.resolution_width
                image_size = (image_size_width, int(screen_height * image_size_width / screen_width))
        else:
            image_size_height = config.resolution_height
            image_size = (int(screen_width * image_size_height / screen_height), image_size_height)
        
        # print(f"Resolution: {image_size}, Original Size: {pygame_screen.get_size()}")
        
        # 创建一个新表面，并将当前屏幕内容缩放到该表面
        scaled_surface = pygame.transform.scale(pygame_screen, image_size)
        
        # 使用pygame.image.save将缩放后的内容保存到文件
        pygame.image.save(scaled_surface, filepath)
        # pygame.image.save(pygame_screen, filepath)
    
    with open(filepath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    time.sleep(0.02)
    
    return filepath, encoded_string

def seed_everything(seed):
    try:
        import random
        random.seed(seed)
    except:
        pass
    try:
        import numpy as np
        np.random.seed(seed)
    except:
        pass        
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
    except:
        pass        