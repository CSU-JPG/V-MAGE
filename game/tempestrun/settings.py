settings = {
    1:{
        "cell_length": 25,
        "speed": 100,
        "random_rate": 0.15,
        "foresight": 180,
        "rotation_speed": 8
    },
    2:{ 
        "cell_length": 20,
        "speed": 120,
        "random_rate": 0.18,
        "foresight": 180,
        "rotation_speed": 8
    },
    3:{
        "cell_length": 15,
        "speed": 140,
        "random_rate": 0.25,
        "foresight": 180,
        "rotation_speed": 8
    },
    4:{
        "cell_length": 15,
        "speed": 160,
        "random_rate": 0.33,
        "foresight": 180,
        "rotation_speed": 8
    },
    5:{
        "cell_length": 15,
        "speed": 200,
        "random_rate": 0.4,
        "foresight": 200,
        "rotation_speed": 8
    }
}



def get_settings(level):
    setting = settings.get(level)
    return setting
    
'''
gen_params = levels.DesignableGenrationParameters(
    cell_length=get_with_warning(level_config, "cell_length", 25),
    speed=get_with_warning(level_config, "speed", 100),
    random_rate=get_with_warning(level_config, "random_rate", 0.15)
)
self.foresight = get_with_warning(level_config, "foresight", 180)
self.rotation_speed = get_with_warning(level_config, "rotation_speed", 8)
'''