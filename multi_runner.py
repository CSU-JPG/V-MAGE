import argparse
import configparser
import importlib
import json
import os
import pathlib
import threading
import time
from runner.game_runner import entry
from utils.config import Config
import wandb
import pandas as pd

config = Config()
    

def get_args_parser():
    
    parser = argparse.ArgumentParser("V-MAGE Agent Runner")
    parser.add_argument("--config_file", type=str, default="./config/tasks_config.json", help="Path to the tasks config JSON file.")
    parser.add_argument("--test_rounds", type=int, default=1, help="Rounds to test the game.")
    parser.add_argument("--output_dir", type=str, default="./runs", help="The path to output the results and log.")
    parser.add_argument("--llmProviderConfig", type=str, help="The path to the LLM provider config file.")
    return parser


def get_local_rank():
  if "LOCAL_RANK" in os.environ:
    return int(os.environ["LOCAL_RANK"])
  if "OMPI_COMM_WORLD_LOCAL_RANK" in os.environ:
    return int(os.environ["OMPI_COMM_WORLD_LOCAL_RANK"])
  return None

def load_tasks_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

if __name__ == '__main__':
    local_rank =  get_local_rank()
    if not local_rank or local_rank == 0:
        parser = get_args_parser()
        args = parser.parse_args()

        # Load tasks configuration from JSON file
        tasks_config = load_tasks_config(args.config_file)
        model_name = args.llmProviderConfig.split("/")[-1].split(".")[0]
        project_name = tasks_config.get('project_name')

        lmm_config = configparser.ConfigParser()
        lmm_config.read(args.llmProviderConfig)
        try:
            model_name = lmm_config.get('lmm', 'model_path')
            model_name = model_name.replace("/", "_")
        except:
            model_name = lmm_config.get('lmm', 'model_name')
        
        wandb.init(
            project="multi_runner_split",

            config={
                "test_rounds": args.test_rounds,
                "output_dir": args.output_dir,
            },
            name=model_name + "_" + project_name,
        )
        
        
        
        
        for task_config in tasks_config["tasks"]:
            
            df = pd.DataFrame(columns=[])
            
            args.gameEnvConfig = task_config.get("gameEnvConfig")
            args.levelConfig = task_config.get("levelConfig")
            
            config.load_env_config(task_config.get("gameEnvConfig"))
            config.load_level_config(task_config.get("levelConfig"))
            
            level_name = args.levelConfig.split("/")[-1].split(".")[0]
            env_name = args.gameEnvConfig.split("/")[-1].split(".")[0]
            
            game_name = config.env_short_name
            
            wandb_run_name = f"{level_name}_{model_name}_{env_name}"
            scores = entry(args, wandb_run_name)
            
            score, valid_rate, prompt_tokens, completion_tokens, total_tokens = \
                [score["score"] for score in scores], \
                [score["valid rate"] for score in scores], \
                [score["prompt_tokens"] for score in scores], \
                [score["completion_tokens"] for score in scores], \
                [score["total_tokens"] for score in scores]
                        
                        
            df[level_name + "_score"] = score
            df[level_name + "_valid_rate"] = valid_rate
            df[level_name + "_prompt_tokens"] = prompt_tokens
            df[level_name + "_completion_tokens"] = completion_tokens
            df[level_name + "_total_tokens"] = total_tokens
            
            csv_filepath = os.path.join(args.output_dir, 'csv_results', game_name)
            pathlib.Path(csv_filepath).mkdir(parents=True, exist_ok=True)
            
            csv_filename = f"{config.env_short_name}_{wandb_run_name}_scores.csv"
            
            csv_filepath = os.path.join(csv_filepath, csv_filename)
            df.to_csv(csv_filepath, index=False)

            wandb.log({csv_filename: df}) 
            
            sum_prompt_tokens = sum([sum(df[key]) for key in df.keys() if "prompt_tokens" in key])
            sum_completion_tokens = sum([sum(df[key]) for key in df.keys() if "completion_tokens" in key])
            sum_total_tokens = sum([sum(df[key]) for key in df.keys() if "total_tokens" in key])
            
            wandb.log({"sum_prompt_tokens": sum_prompt_tokens})
            wandb.log({"sum_completion_tokens": sum_completion_tokens})
            wandb.log({"sum_total_tokens": sum_total_tokens})
        