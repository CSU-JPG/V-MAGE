*link:* [*CSU-JPG V-MAGE Repo*](https://github.com/CSU-JPG/V-MAGE)
---
<br>
<br>

# V-MAGE: A Game Evaluation Framework for Assessing Visual-Centric Capabilities in MLLMs


![](./docs/static/images/overview_5_15.png)


<p align="center">
   <a href="https://csu-jpg.github.io/V-MAGE/" target="_blank">🌐 Project Page</a> | <a href="https://arxiv.org/abs/2504.06148" target="_blank">📃 Paper </a> | <a href="" target="_blank">🤗 Playground </a> 
</p>


## ✨ Introducing **V-MAGE Benchmark**

V-MAGE is a **game-based** benchmark designed to evaluate **visual-centric** capabilities through **flexible gameplay** and **carefully designed levels**. Its defining features are as follows:
  

- **Vision Centric Gameplay**: Models receive only visual input, requiring pixel-level scene understanding, object tracking, and spatial-temporal reasoning. V-MAGE features continuous-space environments, allowing models to explore the almost infinite state space. Each game is deigned with different difficulty levels that targeting various skill dimensions.
- **Extensible Evaluation Framework**: 
V-MAGE extends beyond model evaluation to assess agentic skills that are out-of-scope for current MLLMs. Our game-agent-model three-module evaluation pipeline allows optimizations in both MLLMs and their agent strategies.

- **Adaptive ELO-based Ranking**: 
V-MAGE uses a dynamic Elo system to provide a unified and interpretable metric across diverse games and difficulty levels. Unlike raw scores, which vary in scale across tasks, the Elo rating captures relative skill levels by modeling win–loss dynamics between model performances on shared levels. 


## 📈 Leaderboard 

| Model                  | Pong | Race | Flappybird | Tempestrun | SuperMario | Average |
|------------------------|------|------|------------|------------|------------|---------|
| **Closed-Source Models** |      |      |            |            |            |         |
| Claude-3.7-sonnet      | **1607** | **1626** | **1578**       | 1513       | **1601**       | **1591**    |
| GPT-4o                 | 1487 | 1582 | 1573       | 1514       | 1512       | 1526    |
| Gemini-2.0-Flash (Thinking)| 1518 | 1550 | 1533       | 1498       | 1588       | 1553    |
| Gemini-2.0-Flash       | 1502 | 1498 | 1513       | 1515       | 1512       | 1510    |
| **Open-Source Models** |      |      |            |            |            |         |
| Qwen2VL-7B             | 1464 | 1417 | 1438       | 1488       | 1361       | 1412    |
| Qwen2VL-72B            | 1479 | 1527 | 1521       | 1530       | 1580       | 1543    |
| Qwen2.5VL-72B          | 1485 | 1489 | 1440       | **1531**       | 1509       | 1494    |
| InternVL2.5-8B         | 1489 | 1442 | 1481       | 1471       | 1372       | 1428    |
| InternVL2.5-78B        | 1492 | 1447 | 1481       | 1514       | 1510       | 1510    |
| **Baseline** |      |      |            |            |            |         |
| Random                 | 1477 | 1424 | 1440       | 1424       | 1419       | 1431    |

[Submit](https://github.com/fengxin-zhxx/V-MAGE-Results) your own agent results.

## 🚀 Quick Start

<!-- 启动Evaluation -->
To evaluate model with V-MAGE, you can use the following steps:

### Step 1: Dependencies Installation

Dependencies can be installed via pip:

```bash
cd V-MAGE
conda create -n v-mage python=3.10 -y
conda activate v-mage
pip install -r requirements.txt
```

<!-- 准备模型服务 -->
### Step 2: Model Service

<!-- 如果使用API服务，可以跳过此步骤 -->

**If you are using existing api service, you can skip this step.**

<!-- 我们推荐使用 vLLM 部署 Openai 接口的服务， -->
Otherwise, we recommend using [vLLM](https://github.com/vllm-project/vllm) or [SWIFT](https://github.com/modelscope/ms-swift) to deploy the OpenAI interface service for your local model.


Take vLLM and [Qwen2.5VL-7B Instruct](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct) as an example, you can start the service by running the following command:


```bash
# Download the model. 
# Remember to replace <path-to-model> with the path where you want to save the model.
pip install -U huggingface_hub
huggingface-cli download --resume-download Qwen/Qwen2.5-VL-7B-Instruct --local-dir <path-to-model>

# Start the service. You can change the parameters according to your needs.
pip install vllm
vllm serve <path-to-model> --trust-remote-code --max-model-len 15000 --limit-mm-per-prompt image=6 --port 8000 --gpu-memory-utilization 0.90 --tensor-parallel-size 2

```

You can also use *nohup* to run the service in the background.

### Step3: Config Preparation

Prepare config file for the model service. 

For example, if you are using vLLM, you can simply change the `model_path` and `openai_api_base` in the `config/model_config/openai_service_config.ini`.

```ini
[lmm]
model_name = OpenAI
model_path = <path-to-model>
openai_api_key = EMPTY
openai_api_base = http://localhost:8000/v1 # or your own service address
```

### Step 4: Let's Play!

#### runner.py: To evaluate a single level

```bash
python runner.py \
--llmProviderConfig=./config/model_config/openai_service_config.ini \
--gameEnvConfig=./config/env_config/env_config_race_reasoning_0steps.json \
--levelConfig=./config/level_config/racegame/level1_no_history.json \
--output_dir=runs/Qwen2_5VL_7B \
--test_rounds=10
```

#### multi_runner.py: To evaluate multiple levels

```bash
python multi_runner.py \
--config_file=./config/multi_runner_config/Race_3steps.json \
--llmProviderConfig=./config/model_config/openai_service_config.ini \
--output_dir=runs/Qwen2_5VL_7B \
--test_rounds=10
```

If you don't want to watch the game screen, you can set the environment variable `SDL_VIDEODRIVER` to `dummy` before running the script:

```bash
export SDL_VIDEODRIVER=dummy
```

## 📚 Documentation

### Other Model Providers

will be added soon

<!-- 拓展Agent -->
### Extending Your Own Agent

will be added soon

<!-- 接入新的游戏 -->
### Adding New Games

will be added soon


## 🔗 Others

### Game Codebases

Thanks to the open-source community, we are able to leverage existing game codebases to build our benchmark. Here are the games we used:

| Game  | Codebase |
| --- | --- |
| **RaceGame** | [tdostilio/Race_Game](https://github.com/tdostilio/Race_Game)
| **FlappyBird** | [agneay/pygame-projects/Flappy Bird](https://github.com/agneay/pygame-projects/tree/master/Flappy%20Bird)
| **Pong** | [pyGuru123/Python-Games/Pong](https://github.com/pyGuru123/Python-Games/tree/master/Pong)
| **SuperMario** | [mx0c/super-mario-python](https://github.com/mx0c/super-mario-python)
| **Tempest Run** | [daipenger/pygame-summer-team-jam](https://github.com/davidpendergast/pygame-summer-team-jam)


## 📜 Citation

```
@article{zheng2025vmagebenchmark,
      title={V-MAGE: A Game Evaluation Framework for Assessing Visual-Centric Capabilities in Multimodal Large Language Models}, 
      author={Xiangxi Zheng and Linjie Li and Zhengyuan Yang and Ping Yu and Alex Jinpeng Wang and Rui Yan and Yuan Yao and Lijuan Wang},
      journal={arXiv preprint arXiv:2504.06148},
      year={2025},
}
```


