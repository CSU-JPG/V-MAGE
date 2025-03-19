import random
from game.race.sprites import *


screen_walls = [
     # walls around the screen
    VertivalPadSprite((0, 100)),
    VertivalPadSprite((15, 100)),
    VertivalPadSprite((0, 550)),
    VertivalPadSprite((15, 550)),
    VertivalPadSprite((1024, 100)),
    VertivalPadSprite((1008, 100)),
    VertivalPadSprite((1024, 550)),
    VertivalPadSprite((1008, 550)),
    
    HorizontalPad((60, 0)),
    HorizontalPad((300, 0)),
    HorizontalPad((700, 0)),
    HorizontalPad((900, 0)),
    HorizontalPad((1024, 768)),
    HorizontalPad((624, 768)),
    HorizontalPad((224, 768)),
    
    HorizontalPad((60, 15)),
    HorizontalPad((300, 15)),
    HorizontalPad((700, 15)),
    HorizontalPad((900, 15)),
    HorizontalPad((1024, 753)),
    HorizontalPad((624, 753)),
    HorizontalPad((224, 753))
]

center_square = SquarePadSprite((512, 350))
center_pad = RacePadSprite((512, 350))

settings = {
    1: {
        "pads" : [
            # walls around the screen
            *screen_walls
        ],
        "car_position": (300, 550),
        "trophy_position": (800, 200),
        "direction": 270,              # FACE RIGHT
        "ACCELERATION": 50,            # SPEED UP
        "MAX_FORWARD_SPEED": 20,       # FAST
        "car_image_scale": 0.3,        # BIG
        "trophy_image_scale": 3,       # BIG
        "sample_frame": 1,
        "init_speed": 20,
        "valid_actions": ["LEFT", "RIGHT", "UP", "DOWN"],
        "car_image": "./game/race/images/car_face.png",
        "viewpoint": "map",            # NO TURNING SPEED, JUST MOVE AT THE VIEW OF MAP
        "max_rounds": 100,
    },
    2 : {
        "pads" : [
            # square in the center of the screen
            center_square,
            # walls around the screen
            *screen_walls
        ],
        "car_position": (300, 550),
        "trophy_position": (800, 200),
        "direction": 270,              # FACE RIGHT
        "ACCELERATION": 30,            # SPEED UP
        "MAX_FORWARD_SPEED": 20,       # FAST
        "car_image_scale": 0.3,        # BIG
        "trophy_image_scale": 3,       # BIG
        "sample_frame": 1,
        "init_speed": 20,
        "valid_actions": ["LEFT", "RIGHT", "UP", "DOWN"],
        "car_image": "./game/race/images/car_face.png",
        "viewpoint": "map",            # NO TURNING SPEED, JUST MOVE AT THE VIEW OF MAP
        "max_rounds": 150,
    },
    3:{
        "pads" : [
            # pad in the center of the screen
            center_pad,
            
            # walls around the screen
            *screen_walls
        ],
        "car_position": (300, 550),
        "trophy_position": (800, 200),
        "direction": 270,              # FACE RIGHT
        "ACCELERATION": 30,             # SPEED UP
        "MAX_FORWARD_SPEED": 20,       # FAST
        "car_image_scale": 0.3,        # BIG
        "trophy_image_scale": 3,       # BIG
        "sample_frame": 1,
        "init_speed": 20,
        "valid_actions": ["LEFT", "RIGHT", "UP", "DOWN"],
        "car_image": "./game/race/images/car_face.png",
        "viewpoint": "map",            # NO TURNING SPEED, JUST MOVE AT THE VIEW OF MAP
        "max_rounds": 150,
    },
    
    4:{
        # From bottom to top
        "pads" : [
            # walls around the screen
            *screen_walls
        ],
        "car_position": (300, 550),
        "trophy_position": (800, 200),
        "direction": 0,              # FACE UP
        "ACCELERATION": 30,             # SPEED UP
        "speed_attenuation": 0,        # No speed attenuation
        "MAX_FORWARD_SPEED": 20,       # FAST
        "car_image_scale": 0.3,        # BIG
        "trophy_image_scale": 3,       # BIG
        "sample_frame": 3,
        "valid_actions": ["LEFT", "RIGHT", "FORWARD", "BACKWARD"],
        "car_image": "./game/race/images/white_car.png",
        "viewpoint": "car",           
        "max_rounds": 150,
    },
    5:{
        # From bottom to top
        "pads" : [
            # walls around the screen
            *screen_walls
        ],
        "car_position": (300, 550),
        "trophy_position": (800, 200),
        "direction": 270,              # FACE RIGHT
        "ACCELERATION": 30,             # SPEED UP
        "speed_attenuation": 0,        # No speed attenuation
        "MAX_FORWARD_SPEED": 20,       # FAST
        "car_image_scale": 0.3,        # BIG
        "trophy_image_scale": 3,       # BIG
        "sample_frame": 3,
        "valid_actions": ["LEFT", "RIGHT", "FORWARD", "BACKWARD"],
        "car_image": "./game/race/images/white_car.png",
        "viewpoint": "car",           
        "max_rounds": 150,
    },
    6:{
        "pads" : [
            # walls
            VertivalPadSprite((500, 625)),
            HorizontalPad((250, 375)),
            
            # walls around the screen
            *screen_walls
        ],
        "car_position": (750, 600),
        "MAX_FORWARD_SPEED": 100,
        "speed_attenuation": 0.8,
        "ACCELERATION": 20,
        "direction": 0,
        "trophy_position": (250,120),
        "maximum_time": 20,
        "sample_frame": 1,
    },
    7:{
        "pads" : [
            # walls
            VertivalPadSprite((520, 125)),
            HorizontalPad((280, 375)),
            
            # walls around the screen
            *screen_walls
        ],
        "car_position": (250, 600),
        "MAX_FORWARD_SPEED": 100,
        "speed_attenuation": 0.8,
        "ACCELERATION": 20,
        "direction": 270,
        "trophy_position": (750,120),
        "maximum_time": 20,
        "sample_frame": 1,
    },
    8:{
        "pads" : [
            # walls
            HorizontalPad((0, 10)),
            HorizontalPad((600, 10)),
            HorizontalPad((1100, 10)),
            HorizontalPad((100, 150)),
            HorizontalPad((600, 150)),
            HorizontalPad((100, 300)),
            HorizontalPad((800, 300)),
            HorizontalPad((600, 450)),
            HorizontalPad((1000, 450)),
            HorizontalPad((200, 600)),
            HorizontalPad((900, 600)),
            
            # walls around the screen
            *screen_walls
        ],
        "car_position": (250, 680),
        "MAX_FORWARD_SPEED": 30,
        "speed_attenuation": 0.8,
        "ACCELERATION": 10,
        "direction": 0,
        "trophy_position": (750,50),
        "maximum_time": 20,
        "sample_frame": 1,
        "car_image_scale": 0.07,
        "max_rounds": 300,
    },
    9:{
        "pads" : [
            # walls
            VertivalPadSprite((0, 200)),
            VertivalPadSprite((0, 400)),
            HorizontalPad((60, 0)),
            HorizontalPad((300, 0)),
            HorizontalPad((700, 0)),
            HorizontalPad((900, 0)),
            VertivalPadSprite((1024, 100)),
            VertivalPadSprite((1024, 550)),
            HorizontalPad((1024, 768)),
            HorizontalPad((624, 768)),
            HorizontalPad((224, 768)),
            VertivalPadSprite((200, 768)),
            VertivalPadSprite((200, 368)),
            HorizontalPad((450, 130)),
            HorizontalPad((550, 130)),
            VertivalPadSprite((800, 375)),
            SmallHorizontalPad((670, 615)),
            SmallHorizontalPad((470, 615)),
            SmallVerticalPad((350, 490)),
            SmallVerticalPad((350, 390)),
            SmallHorizontalPad((470, 270)),
            SmallVerticalPad((600, 390)),
            
            # walls around the screen
            *screen_walls
        ],
        "car_position": (80, 650),
        "MAX_FORWARD_SPEED": 30,
        "speed_attenuation": 0.8,
        "ACCELERATION": 10,
        "direction": 0,
        "trophy_position": (450,320),
        "maximum_time": 20,
        "sample_frame": 1,
        "car_image_scale": 0.07,
        "max_rounds": 500,
    },
}

def dynamic_update(setting, level):
    
    if level in [1, 2, 3]:
        
        car_y = random.randint(200, 600)
        ranges = []
        if car_y - 100 >= 200:
            ranges.append((max(200, car_y - 420), car_y - 100))
        if car_y + 100 <= 600:
            ranges.append((car_y + 100, min(600, car_y + 420)))
        selected_range = random.choice(ranges)
        trophy_y = random.randint(selected_range[0], selected_range[1])
        
        # 随机决定左右镜像
        if random.choice([True, False]):
            car_x = 800
            trophy_x = 300
        else:
            car_x = 300
            trophy_x = 800
        
        setting["car_position"] = (car_x, car_y)
        setting["trophy_position"] = (trophy_x, trophy_y)
        
        if level == 2:
            # put SquarePadSprite in the middle of the car and the trophy
            setting["pads"][0] = SquarePadSprite(((car_x + trophy_x) / 2, (car_y + trophy_y) / 2))

            
        if level == 3:
            # randomly put a vertical or horizontal wall in the middle of the car and the trophy
            if random.choice([True, False]):
                setting["pads"][0] = SmallVerticalPad(((car_x + trophy_x) / 2, (car_y + trophy_y) / 2))

            else:
                setting["pads"][0] = SmallHorizontalPad(((car_x + trophy_x) / 2, (car_y + trophy_y) / 2))
    
    if level == 4:
        car_x = random.randint(200, 800)
        ranges = []
        if car_x - 180 >= 200:
            ranges.append((max(200, car_x - 420), car_x - 180))
        if car_x + 180 <= 800:
            ranges.append((car_x + 180, min(800, car_x + 420)))
        selected_range = random.choice(ranges)
        trophy_x = random.randint(selected_range[0], selected_range[1])
        setting["car_position"] = (car_x, 550)
        setting["trophy_position"] = (trophy_x, 100)
        
    if level in[5]:
        car_y = random.randint(200, 600)
        ranges = []
        if car_y - 100 >= 200:
            ranges.append((max(200, car_y - 420), car_y - 100))
        if car_y + 100 <= 600:
            ranges.append((car_y + 100, min(600, car_y + 420)))
        selected_range = random.choice(ranges)
        trophy_y = random.randint(selected_range[0], selected_range[1])
        
        if random.choice([True, False]):
            setting["direction"] = 90
            setting["car_position"] = (800, car_y)
            setting["trophy_position"] = (300, trophy_y)
        else:
            setting["direction"] = 270
            setting["car_position"] = (300, car_y)
            setting["trophy_position"] = (800, trophy_y)
    
    if level in [6]:
        if random.choice([True, False]):
            setting["pads"][0] = VertivalPadSprite((500, 625))
            setting["pads"][1] = HorizontalPad((250, 375))
            setting["car_position"] = (750, 600)
            setting["trophy_position"] = (250,120)
        else:
            setting["pads"][0] = VertivalPadSprite((530, 625))
            setting["pads"][1] = HorizontalPad((770, 375))
            setting["car_position"] = (250, 600)
            setting["trophy_position"] = (750,120)
    
    if level in [7]:
        # if random.choice([True, False]):
        #     setting["pads"][0] = VertivalPadSprite((520, 125))
        #     setting["pads"][1] = HorizontalPad((280, 375))
        #     setting["car_position"] = (250, 600)
            # setting["direction"] = 270
        #     setting["trophy_position"] = (750,120)
        # else:
        setting["pads"][0] = VertivalPadSprite((500, 125))
        setting["pads"][1] = HorizontalPad((740, 375))
        setting["car_position"] = (750, 600)
        setting["trophy_position"] = (250,120)
        setting["direction"] = 90
    
    return setting

def get_settings(level, dynamic=False):
    setting = settings.get(level)
    if not dynamic:
        return setting
    
    # dynamic settings
    return dynamic_update(setting, level)
    