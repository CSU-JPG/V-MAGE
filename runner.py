import argparse
import importlib
import os
import pathlib
import threading
import time

import pandas as pd
from runner.game_runner import entry
from utils.config import Config
import wandb
import configparser

config = Config()

def main(args):
  
    lmm_config = configparser.ConfigParser()
    lmm_config.read(args.llmProviderConfig)
    
    model_name = args.llmProviderConfig.split("/")[-1].split(".")[0]
    
    try:
      model_name = lmm_config.get('lmm', 'model_path')
      model_name = model_name.replace("/", "_")
    except:
      model_name = lmm_config.get('lmm', 'model_name')
    
    level_name = args.levelConfig.split("/")[-1].split(".")[0]
    
    env_name = args.gameEnvConfig.split("/")[-1].split(".")[0]

    game_name = config.env_short_name
    
    wandb_run_name = f"{level_name}_{model_name}_{env_name}"

    wandb.init(
        project=f"V-MAGE-Game-{config.env_short_name.lower()}",

        config={
          "llmProviderConfig": args.llmProviderConfig,
          "gameEnvConfig": args.gameEnvConfig,
          "levelConfig": args.levelConfig,
          "test_rounds": args.test_rounds,
          "output_dir": args.output_dir,
        },
        name=wandb_run_name,
    )

    scores = entry(args, wandb_run_name)
    score, valid_rate = [score["score"] for score in scores], [score["valid rate"] for score in scores]
    
    prompt_tokens, completion_tokens, total_tokens = \
      [score["prompt_tokens"] for score in scores], \
      [score["completion_tokens"] for score in scores], \
      [score["total_tokens"] for score in scores]
    
    df = pd.DataFrame(columns=[])
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
    
    print("Results saved to", csv_filepath)
    
    wandb.log({csv_filename: df}) 


def get_args_parser():

    parser = argparse.ArgumentParser("V-MAGE Agent Runner")
    parser.add_argument("--llmProviderConfig", type=str, default="./config/gpt_server_config.ini", help="The path to the LLM provider config file.")
    parser.add_argument("--gameEnvConfig", type=str, default="./config/env_config/3steps/env_config_race.json", help="The path to the environment config file.")
    parser.add_argument("--levelConfig", type=str, default="./config/level_config/racegame/level1.json", help="The path to the level config file.")
    
    
    parser.add_argument("--generationConfig", type=str, default="./config/model_config/generation_config.ini", help="The path to the generation config file.")
    
    parser.add_argument("--test_rounds", type=int, default=1, help="Rounds to test the game.")
    
    parser.add_argument("--output_dir", type=str, default="./runs", help="The path to output the results and log.")
    
    return parser


def get_local_rank():
  if "LOCAL_RANK" in os.environ:
    return int(os.environ["LOCAL_RANK"])
  if "OMPI_COMM_WORLD_LOCAL_RANK" in os.environ:
    return int(os.environ["OMPI_COMM_WORLD_LOCAL_RANK"])
  return None


if __name__ == '__main__':
    local_rank =  get_local_rank()
    if not local_rank or local_rank == 0:
        parser = get_args_parser()
        args = parser.parse_args()

        config.load_env_config(args.gameEnvConfig)
        config.load_level_config(args.levelConfig)

        main(args)



