import pygame


def pygame_image_scale(pygame_loaded_image, scale_factor):

    # 获取原始图像的尺寸
    original_size = pygame_loaded_image.get_size()
    original_width, original_height = original_size

    # 计算新的尺寸
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    new_size = (new_width, new_height)

    # 按比例缩放图像
    image = pygame.transform.scale(pygame_loaded_image, new_size)
    
    return image


def get_distance(car: pygame.sprite.Sprite, trophy: pygame.sprite.Sprite): 
    return ((car.rect.x - trophy.rect.x) ** 2 + (car.rect.y - trophy.rect.y) ** 2) ** 0.5
    