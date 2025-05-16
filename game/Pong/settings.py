

settings = {
    1:{
        "paddle": (10, 200),
        "ball_size": 40,
        "paddle_speed": 5,
        "ball_speed": 4
    },
    2:{
        "paddle": (10, 150),
        "ball_size": 30,
        "paddle_speed": 8,
        "ball_speed": 8
    },
    3:{
        "paddle": (10, 100),
        "ball_size": 20,
        "paddle_speed": 10,
        "ball_speed": 12
    }
}



def get_settings(level):
    setting = settings.get(level)
    return setting
    