import queue
import random
import re
from time import sleep
from typing import Dict
from utils.config import Config
from utils.dict_utils import kget
from utils.encoding_utils import encode_data_to_base64_path, encode_image_path
from utils.file_utils import assemble_project_path, get_all_files
from utils.json_utils import parse_semi_formatted_text
from utils.lmm_utils import assemble_prompt
from utils.planner_utils import _extract_keys_from_template
import json
import wandb
import pickle
import os
import time

config = Config()


class game_agent:
    def __init__(self, llm_provider):
        # if config has attribute level_prompt, use it, otherwise use default prompt
        if hasattr(config, "level_prompt") and config.level_prompt is not None:
            self.prompt = config.level_prompt
        else:
            self.prompt = config.prompt
        
        
        self.prompt_template_origin, _, _ = _extract_keys_from_template(self.prompt)
        self.prompt_template = self.prompt_template_origin
        
        self.use_instruction = config.use_instruction
        if self.use_instruction:
            self.instruction_template = config.instruction
        
        self.use_history = config.use_history
        if self.use_history:
            self.history_template = config.history
            
            self.history_size = len([image_history for image_history in self.history_template if "image" in image_history])
            self.history = []
            
            self.use_sample_history = config.use_sample_history
            
            if self.use_sample_history:
                self.sample_size = config.sample_size
                self.sample_histroy_template = config.sample_histroy_template
            
        else:
            self.history_size = 1
            self.history = []
        
        self.reset_provider(llm_provider)
        
        self.response_record = []
        
        
    
    def reset_provider(self, llm_provider):
        self.llm_provider = llm_provider
        if self.history is not None and len(self.history) > 0:
            # pop the last history
            self.history.pop(-1)
            
    
    def produce_instruction(self): 
        """
        Generates and inserts an instruction string into the prompt template.
        This method constructs an instruction string based on the `instruction_template` attribute.
        It replaces the placeholder "<$instruction$>" in the `prompt_template` with the generated instruction string.
        The instruction string is built by iterating over the `instruction_template` list, appending text and encoded image placeholders as needed.
        Raises:
            AssertionError: If the placeholder "<$instruction$>" is not found in `prompt_template`.
        Side Effects:
            Modifies `self.prompt_template` by replacing the "<$instruction$>" placeholder with the generated instruction string.
            Updates `self.input` with encoded image paths using placeholders like "image_instruction_{counter}".
        """
        assert "<$instruction$>" in self.prompt_template
        
        instruction_str = ""
        instruction_str += "\n\n" + self.instruction_template[0]["text"]
        counter = 1
        for item in self.instruction_template[1:]:
            instruction_str += "\n\n"
            if "image" in item:
                placeholder_token = f"image_instruction_{counter}"
                self.input[placeholder_token] = encode_image_path(item["image"])
                instruction_str += f"<${placeholder_token}$>"
            if "text" in item:
                instruction_str += item["text"]
            counter += 1
        
        self.prompt_template = self.prompt_template.replace("<$instruction$>", instruction_str + "\n\n")
    
    def produce_history(self):
        """
        Generates a history string based on the provided history template and updates the prompt template with this history.
        The method processes the `history_template` in reverse order (excluding the first element) and constructs a history string by replacing placeholders with corresponding values from the `history` list. It also updates the `input` dictionary with image history placeholders.
        The constructed history string is then inserted into the `prompt_template` at the placeholder "<$history$>".
        Raises:
            AssertionError: If the placeholder "<$history$>" is not found in `prompt_template`.
        """
        assert "<$history$>" in self.prompt_template
        
        history_str = ""
        
        # Note: The history is stored in reverse order, with the most recent step at the end of the list.
        
        ########################################################################################
        # produce recent history
        
        # skip current step
        counter = 2
        
        for item in reversed(self.history_template[1:]):
            if counter > len(self.history):
                break
            # reversed
            if "text" in item:
                history_text_template = item["text"]
                for history_variable in self.history[-counter]:
                    if history_variable == "image":
                        continue
                    
                    # history_variable_X is the X step in the past (X == 1 means the previous step)
                    history_variable_X = f"{history_variable}_{counter-1}"
                    placeholder_token = f"<${history_variable_X}$>"
                    if placeholder_token in history_text_template:
                        history_text_template = \
                            history_text_template.replace(placeholder_token, self.history[-counter][history_variable])
                history_str = history_text_template + history_str
                
            if "image" in item:
                placeholder_token = f"image_history_{counter}"
                self.input[placeholder_token] = self.history[-counter]["image"]
                history_str = f"<${placeholder_token}$>" + history_str
                
            
            history_str = "\n\n" + history_str
            
            counter += 1
            
        ########################################################################################
        # produce sample history
        
        # a naive implementation
        # just randomly select a sample from the history before self.history_size steps of the current step
        
        if self.use_sample_history:
            
            
            sample_size = min(self.sample_size, max(len(self.history) - self.history_size,  0))
            sample_index = random.sample(range(0, len(self.history)- self.history_size), sample_size)
            
            sample_index.sort(reverse=True)
            
            sample_history_str = ""
            for index in sample_index:
                '''
                This screenshot is <$sample_step$> steps before the current step of the game. After this frame, your reasoning message was \"<$sample_history_reasoning$>\". After the action was excuted, the game info was \"<$sample_history_action_info$>\"
                '''
                sample_history_template = self.sample_histroy_template["text"]
                # 0 1 2  [3 4]  5 (cur)        (index)
                
                for history_variable in self.history[index]:
                    if history_variable == "image":
                        continue
                    sample_history_variable = f"sample_{history_variable}"
                    placeholder_token = f"<${sample_history_variable}$>"
                    if placeholder_token in sample_history_template:
                        sample_history_template = \
                            sample_history_template.replace(placeholder_token, self.history[index][history_variable])
                    
                sample_history_template = sample_history_template.replace("<$sample_step$>", str(len(self.history) - index))

                placeholder_token_image = f"image_sample_{index}"

                sample_history_image = self.history[index]["image"]
                self.input[placeholder_token_image] = sample_history_image
                
                history_str = "\n\n" + f"<${placeholder_token_image}$>" + sample_history_template + history_str 
        
        ########################################################################################
        
            
        if len(self.history) != 0:
            history_str = "\n\n" + self.history_template[0]["text"] + history_str
            
        self.prompt_template = self.prompt_template.replace("<$history$>", history_str + "\n\n")
        
        if len(self.history) == 10:
            sleep(100)
        
    def update_recent_history(self, info: Dict):
        # Update the last step with the action taken
        if len(self.history) == 0:
            return
        # for key in ["history_action", "history_action_info", "history_reasoning"]:
        for key in info.keys():
            if info.get(key) is not None:
                self.history[-1][key] = info[key]
                
    def update_new_history(self, info: Dict):
        self.history.append({
            # Current Step
            'image': info["last_frame_base64"],
            'image_path': info["last_frame_path"],
            'history_action': None,
            'history_action_info': None,
            'history_reasoning': None
        })
        
        if self.use_history and not self.use_sample_history and len(self.history) > self.history_size + 1:
            self.history.pop(0)
    
    
    def update_game_info(self, game_info: Dict):
        # TODO: working memory module
        # e.g. 
        # self.memory.update(info)
        
        self.update_recent_history(game_info)
        self.update_new_history(game_info)
    
    def generate_input(self):
        self.input = {}
        self.prompt_template = self.prompt_template_origin
        
        # current step image is at the end of the history
        self.input['image_current_step'] = self.history[-1]["image"]
        
        # Instruction
        if self.use_instruction:
            # replace <$instruction$> with images and texts.
            self.produce_instruction()
        
        # History
        if self.use_history:
            # replace <$history$> with images and texts.
            self.produce_history()
            
    def generate_action(self, data):
        
        if data.get("action") is None:
            data["action"] = "None"
            
        action = data["action"]

        return action
    
    def execute_action(self):
        # Generate self.input
        self.generate_input()
        
        # Generate prompt
        message_prompts = assemble_prompt(template_str=self.prompt_template, params=self.input, image_prompt_format=self.llm_provider.image_prompt_format)
        
        # Replace base64 image data with values from history array
        readable_message_prompts = json.dumps(message_prompts, indent=2)
        pattern = re.compile(r"\"data:image/png;base64,[^\"]*\"")
        
        # Call the LLM provider for decision making
        response = self.llm_provider.create_completion(message_prompts)
        
        save = config.save_response
        
        if save:
            self.response_record.append({
                "message": message_prompts, 
                "response": response, 
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),
                "model": self.llm_provider.model_path,
                "env": config.env_name,
                "level": kget(config.level_config, 'level', default=None)
            })
            
            if len(self.response_record) % 500 == 0:
                self.save_response_record()
                    
        
        response = response.replace("#", "")
        response = re.sub(r'\n+', '\n', response)
        
        # Convert the response to dict
        response = response.replace(":", ":\n")
        
        data = parse_semi_formatted_text(response)
        
        self.update_recent_history({"history_reasoning": str(data)})
        
        action = self.generate_action(data)
        
        return action
    
    def save_response_record(self):
        save_dir = os.path.join(config.output_dir, 'response_record')
        os.makedirs(save_dir, exist_ok=True)
        config_name = config.env_config_path.split('config/env_config/')[-1].replace('.json', '').replace('/', '_')
        model_name = self.llm_provider.model_path.replace('/', '_').replace('.', '_')
        save_path = os.path.join(save_dir, f"{model_name}_{config_name}.pkl")

        all_record = []
        with open(save_path, "ab+") as f: 
            try:
                import fcntl
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)

                f.seek(0)
                try:
                    if os.path.getsize(save_path) > 0:
                        all_record = pickle.load(f)
                except EOFError:
                    all_record = [] 
                except Exception as e:
                    print(f"Error loading existing records: {e}")
                    all_record = [] 

                all_record.extend(self.response_record)

                f.seek(0)
                f.truncate()
                pickle.dump(all_record, f)
                print("save record, now count:", len(all_record), " save_path: ", save_path)

            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        