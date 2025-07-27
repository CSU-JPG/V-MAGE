import os
import time
from utils import Singleton
from utils.file_utils import assemble_project_path, get_project_root
from utils.json_utils import load_json
from utils.dict_utils import kget


class Config(metaclass=Singleton):
    
    # work_dir = './runs'
    FPS = 30
    save_response = False
    output_dir  = './runs'
    extra_config = {}
    
    
    """
    Configuration class.
    """
    def load_env_config(self, env_config_path):
        
        # Ensure env_config_path exists
        if not os.path.exists(env_config_path):
            raise FileNotFoundError(f"Level config path {env_config_path} does not exist.")
        
        self.env_config_path = env_config_path
        # 加载游戏参数
        path = assemble_project_path(env_config_path)
        self.env_config = load_json(path)
        
        self.env_name = kget(self.env_config, 'env_name', default='')
        self.env_short_name = kget(self.env_config, 'env_short_name', default='')
        
        self.game_module = kget(self.env_config, 'game_module', default='')
        self.game_class = kget(self.env_config, 'game_class', default='')
        
        
        # self.work_dir = assemble_project_path(os.path.join(self.work_dir, str(time.time())))
        
        self.use_instruction = kget(self.env_config, 'use_instruction', default='False') == "True"
        if self.use_instruction:
            self.instruction = []
            for item in kget(self.env_config, 'instruction', default=[]):
                instruction_content = {}
                if "text" in item:
                    instruction_content["text"] = item["text"]
                if "image" in item:
                    instruction_content["image"] = item["image"]
                self.instruction.append(instruction_content)
    

        self.use_history = kget(self.env_config, 'use_history', default='False') == "True"
        if self.use_history:
            self.history = []
            for item in kget(self.env_config, 'history', default=[]):
                history_content = {}
                if "text" in item:
                    history_content["text"] = item["text"]
                if "image" in item:
                    history_content["image"] = item["image"]
                self.history.append(history_content)
            
            self.use_sample_history = kget(self.env_config, "use_sample_history", default="False") == "True"
            
            if self.use_sample_history:
                self.sample_size = int(kget(self.env_config, "sample_size", default=0))
                
                self.sample_histroy_template = kget(self.env_config, "sample_histroy_template", default={})
                
                
                
                
        
        self.prompt = kget(self.env_config, 'prompt', default='')
        self.instruction_images = kget(self.env_config, 'instruction_images', default='Error')
        
        self.resolution_height = kget(self.env_config, 'resolution_height', default=360)
        self.resolution_width = kget(self.env_config, 'resolution_width', default=-1)
        
    def load_level_config(self, level_config_path):
        # Ensure level_config_path exists
        if not os.path.exists(level_config_path):
            self.level_config = None
            return  
        
        # 加载关卡参数
        path = assemble_project_path(level_config_path)
        self.level_config = load_json(path)
        
        self.level_prompt = kget(self.level_config, 'level_prompt', default=None)