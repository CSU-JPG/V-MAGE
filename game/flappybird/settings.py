import random
from game.race.sprites import *


settings = {
    1: {
        "valid_actions": ["UP", "DOWN", "KEEP"],
        "jump_height": 7,
        "gravity": 0,
        "move_speed": 5,
        "pipe_gap": 400,
        "pipe_frequency": 70,
        "sample_frame": 5,
        "rotate": False,
	},
    2: {
        "valid_actions": ["UP", "DOWN", "KEEP"],
        "jump_height": 7,
        "gravity": 0,
        "move_speed": 5,
        "pipe_gap": 270,
        "pipe_frequency": 70,
        "sample_frame": 5,
        "rotate": False,
	},
    3: {
        "valid_actions": ["UP", "DOWN", "KEEP"],
        "jump_height": 7,
        "gravity": 0,
        "move_speed": 10,
        "pipe_gap": 270,
        "pipe_frequency": 50,
        "sample_frame": 5,
        "rotate": False,
	},
    4: {
        "valid_actions": ["UP", "KEEP", "NONE"],
        "jump_height": 7,
        "gravity": 0.25,
        "move_speed": 5,
        "pipe_gap": 350,
        "pipe_frequency": 70,
        "sample_frame": 3,
        "rotate": False,
	},
    5: {
        "valid_actions": ["UP", "KEEP", "NONE"],
        "jump_height": 7,
        "gravity": 0.25,
        "move_speed": 5,
        "pipe_gap": 350,
        "pipe_frequency": 70,
        "sample_frame": 3,
        "rotate": False,
	},
    6: {
        "valid_actions": ["UP", "KEEP", "NONE"],
        "jump_height": 7,
        "gravity": 0.25,
        "move_speed": 5,
        "pipe_gap": 350,
        "pipe_frequency": 70,
        "sample_frame": 3,
        "rotate": False,
	},
    
    7: {
        "valid_actions": ["UP", "NONE"],
        "jump_height": 7,
        "gravity": 0.25,
        "move_speed": 5,
        "pipe_gap": 400,
        "pipe_frequency": 70,
        "sample_frame": 3,
        "rotate": False,
	},
        

}


def get_settings(level):
    setting = settings.get(level)
    return setting
    