import configparser
import time
from typing import Any, Dict, List
from datetime import datetime


class ClaudeProvider:
    
    def __init__(self, llm_provider_config_path, generation_config_path="./config/model_config/generation_config.ini") -> None:
        self.llm_provider_config_path = llm_provider_config_path
    
        self.llm_config = configparser.ConfigParser()
        self.llm_config.read(llm_provider_config_path)
        
        self.generation_config = configparser.ConfigParser()
        self.generation_config.read(generation_config_path)
        
        self.model_path = self.llm_config.get('lmm', 'model_path')
        self.api_key = self.llm_config.get('lmm', 'api_key')
  
        self.image_prompt_format = "claude"
        
        # Generation config
        self.top_p = float(self.generation_config.get('generation', 'top_p'))
        self.temperature = float(self.generation_config.get('generation', 'temperature'))
        self.max_new_tokens = int(self.generation_config.get('generation', 'max_new_tokens'))
        
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
    
    def reset(self):
        self.llm_config.read(self.llm_provider_config_path)
        self.model_path = self.llm_config.get('lmm', 'model_path')
        self.api_key = self.llm_config.get('lmm', 'api_key')   

    
    def get_tokens_usage(self):
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }
    
    def create_completion(self, message_prompts):        
        import anthropic
        while True:
            try:
                client = anthropic.Anthropic(
                    api_key=self.api_key
                )
                
                chat_response = client.messages.create(
                    model=self.model_path, 
                    max_tokens=self.max_new_tokens,
                    messages=message_prompts,
                    temperature=self.temperature,
                    top_p=self.top_p
                )
                
                response_text = chat_response.content[0].text
                
                prompt_tokens = chat_response.usage.input_tokens
                completion_tokens = chat_response.usage.output_tokens
                # 输出token使用统计
                total_tokens = prompt_tokens + completion_tokens
                
                self.prompt_tokens += prompt_tokens
                self.completion_tokens += completion_tokens
                self.total_tokens += total_tokens
                break
            except Exception as e:
                time.sleep(5)
                self.reset()
                
                
        return response_text