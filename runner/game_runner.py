from datetime import datetime
import importlib
import os
import pathlib
import queue
import random
import threading
import time

import tqdm

from agent.game_agent import game_agent

from utils.game_utils import seed_everything
import wandb
from provider.ProviderFactory import ProviderFactory
from utils.calculate_log import calculate_statistics, extract_scores
from utils.config import Config
from utils.encoding_utils import encode_data_to_base64_path
from utils.file_utils import assemble_project_path, get_all_files, img_to_gif, run_path_construct
from utils.json_utils import parse_semi_formatted_text
from utils.lmm_utils import assemble_prompt
from utils.planner_utils import _extract_keys_from_template
import pickle

config = Config()


class GamePipelineRunner():
    def __init__(self,
                 args):
        # TODO add more mesages in run path. e.g. guide/instruction/..
        run_path = run_path_construct(
            args.output_dir, 
            config.env_short_name, 
            args.levelConfig.split('/')[-1].split(".")[0],
            args.llmProviderConfig.split('/')[-1].split(".")[0],
            datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        )
        self.record_path = args.output_dir
        self.output_dir = assemble_project_path(run_path)
        pathlib.Path(self.output_dir).mkdir(parents=True, exist_ok=True) 
        
        self.env_name = config.env_name
        self.game_module = config.game_module
        self.game_class = config.game_class
        
        self.llm_provider_config_path = args.llmProviderConfig
        self.llm_provider = None
        
        self.agent = None
        self.reset()
        
    def reset(self):
        if self.llm_provider:
            self.llm_provider.reset()
        else:
            self.llm_provider = ProviderFactory.getProvider(self.llm_provider_config_path)
        
        if self.agent is None:
            self.agent = game_agent(self.llm_provider)
        else:
            self.agent.reset_provider(self.llm_provider)
        
    def input_listener(self, event):
        # self.reset()
        count = 0
        while not event.is_set() and not self.game.over:  # 添加运行状态检查
            if not self.game.new_action_event.is_set():
                # 生成动作并通知主线程
                game_info = self.game.get_game_info()
                self.agent.update_game_info(game_info)
                if not self.llm_provider:
                    action = random.choice(self.game.valid_actions)
                    time.sleep(0.5)
                else:
                    action = self.agent.execute_action()
                self.game.current_action = action
                self.game.new_action_event.set()  # 设置事件表示有新动作
            else:
                count += 1
            time.sleep(0.02)
             
    def run(self):
        
        game_module = importlib.import_module(self.game_module)
        game_class = getattr(game_module, self.game_class)
        self.game = game_class(self.output_dir)
        
        self.game.run(self.input_listener)
        
        scores = self.game.get_score()
        token_usage = self.llm_provider.get_tokens_usage()
        
        # merge scores and token_usage
        scores.update(token_usage)
        
        return scores, self.game.game_frames
        
    def pipeline_shutdown(self):
        self.agent = None
        pass


def entry(args, run_name=""):
    
    
    pipelineRunner = GamePipelineRunner(args)
    
    pickle_record_path = os.path.join(pipelineRunner.record_path, config.env_short_name, f"record_{run_name}.pickle") 
    directory = os.path.dirname(pickle_record_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
        
    if os.path.exists(pickle_record_path):
        scores = pickle.load(open(pickle_record_path, "rb"))
        
    else:
        scores = []
        pickle.dump(scores, open(pickle_record_path, "wb"))
            
    
    
    
    with tqdm.tqdm(total=args.test_rounds, initial=len(scores), desc=run_name) as pbar:
        for test_round in range(len(scores), args.test_rounds): 
            
            pipelineRunner.reset()
            
            seed_everything(test_round)
            
            config.pbar = pbar
            
            now_avg_score = 0 if len(scores) == 0 else sum([score["score"] for score in scores])/len(scores)
            now_avg_score = round(now_avg_score, 2)
            config.now_avg_score = now_avg_score
            
            score_dict, game_frames = pipelineRunner.run()
            pbar.update()
            
            scores.append(score_dict)
            
            pipelineRunner.pipeline_shutdown()
            
            game_frames_gif = os.path.join(pipelineRunner.output_dir, datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + ".gif")
            img_to_gif(game_frames, game_frames_gif)
            
            
            log_dict = {"round" : test_round}
            # 按dict 统计分数
            for key in score_dict:
                log_dict.update({
                    run_name + "_" + key: score_dict[key],
                    run_name + "_avg_" + key: sum([score[key] for score in scores])/len(scores)
                })
            
            log_dict.update({"image": wandb.Image(game_frames_gif)})
                
            wandb.log(log_dict)
            
            pickle.dump(scores, open(pickle_record_path, "wb"))
        
        
        now_avg_score = 0 if len(scores) == 0 else sum([score["score"] for score in scores])/len(scores)
        now_avg_score = round(now_avg_score, 2)
        config.now_avg_score = now_avg_score
        
        pbar.set_postfix(
            avg_score=config.now_avg_score
        )
        
    return scores