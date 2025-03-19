from abc import ABC, abstractmethod
import random
import threading
import time
import pygame
import tqdm

from utils.config import Config
from utils.game_utils import capture

config = Config()


class PygameBase(ABC):
    @abstractmethod
    def __init__(self, output_dir, name):
        """Initialize the game, including setting up the game board, player, and environment."""
        
        self.output_dir = output_dir
        self.last_frame_base64 = None
        self.last_frame_path = None
        self.clock = pygame.time.Clock()
        
        # Load the level config, should be in Dict format
        self.level_config = config.level_config
        self.set_level_config(self.level_config)
        
        
        # pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.init()
        
        self.over = False
        self.score = 0
        
        self.new_action_event = threading.Event()  # 用于通知有新动作
        self.new_action_event.set()
        
        self.history_frame_base64 = None
        self.history_action = None
        self.history_action_info = None
        self.history_valid_action = None
        self.action_in_sample_frames = None
        self.invalid_action_count = 0
        
        self.game_frames = []
        
        self.sample_frames = 3
        
        pygame.display.set_caption(name)
        

    @abstractmethod
    def step(self, action, dt=None):
        """
        Perform one step in the game based on the action taken.
        :param action: Action to be performed (could be direction, button press, etc.)
        :return: (done: bool, info: Any) Whether the game is over and any additional info, such as score.
        """
        pass
    
    
    @abstractmethod
    def human_mode_action(self, event):
        """
        Get the action from human player.
        :param event: pygame event
        :return: action: str
        """
        pass
    
    def get_score(self):
        """
        Retrieve the current score.
        Returns:
            int: The current score.
        """
        return self.score
    
    def get_game_info(self):
        #TODO: history should be managed by agent, not game
        info = {
            # Last step info
            "history_action": self.history_action,
            "history_frame_base64": self.history_frame_base64,
            "history_action_info": self.history_action_info,
            
            # Current step info
            "last_frame_base64": self.last_frame_base64,
            "last_frame_path": self.last_frame_path,
        }
        return info
    
    def init_run(self):
        
        self.step("None", 0)
        
        filepath, encoded_string = capture(self.screen, self.output_dir)
        self.last_frame_path=filepath
        self.last_frame_base64 = encoded_string
        self.game_frames.append(filepath)
        self.history_frame_base64 = self.last_frame_base64
        self.history_action = "None"
        self.history_action_info = "Game Initialization."
        self.history_valid_action = "None"
    
    def run(self, input_thread_method, human_mode=False):
        thread_event = threading.Event()
        if not human_mode:
            input_thread = threading.Thread(target=input_thread_method, args=(thread_event,), daemon=True)
            input_thread.start()
            
        self.init_run()
        
        waiting_time = 0
        invalid_action_count_temp = 0
        self.new_action_event.clear()  # 清除事件，准备接收下一个动作
        frame = 0
        frame_flag = True
        
        
        while not self.over:
            config.pbar.set_postfix(avg_score=config.now_avg_score, score=self.score, frames=len(self.game_frames))
            dt = 0.033
            self.clock.tick(config.FPS)
            
            if not frame_flag:
                frame += 1
                if frame != self.sample_frames:
                    step_action = self.history_valid_action
                    if self.action_in_sample_frames is not None:
                        step_action = self.action_in_sample_frames
                        
                    done, info = self.step(step_action, dt)
                    if done:
                        self.over = True
                        break
                        
                    self.history_action_info = info
                    filepath, encoded_string = capture(self.screen, self.output_dir)
                    self.last_frame_path=filepath
                    self.last_frame_base64 = encoded_string
                    self.game_frames.append(filepath)
                    continue
                else:
                    frame = 0   
                    if not human_mode:
                        self.new_action_event.clear()  # 清除事件，准备接收下一个动作 
                    frame_flag = True

            if not human_mode:
                if not input_thread.is_alive():
                    thread_event = threading.Event()
                    input_thread = threading.Thread(target=input_thread_method, args=(thread_event,), daemon=True)
                    time.sleep(5)
                    input_thread.start()
            
            # human_mode
            # if not self.new_action_event.is_set():
            action = None
            for event in pygame.event.get():
                action = self.human_mode_action(event)
                if action is None or action not in self.valid_actions:
                    continue
                done, info = self.step(action, dt)
                frame_flag = False
                # History
                self.history_frame_base64 = self.last_frame_base64
                self.history_action = action
                self.history_valid_action = action
                self.history_action_info = info
                filepath, encoded_string = capture(self.screen, self.output_dir)
                self.last_frame_path=filepath
                self.last_frame_base64 = encoded_string
                self.game_frames.append(filepath)
                    
                waiting_time = 0
            
            # 从队列中获取动作
            if self.new_action_event.is_set():
                waiting_time = 0
                action = self.current_action
                self.current_action = None
                
                if action in self.valid_actions:
                    # Valid action
                    done, info = self.step(action, dt)

                    # History
                    self.history_frame_base64 = self.last_frame_base64
                    self.history_action = action
                    self.history_action_info = info
                    self.history_valid_action = action
                    
                    
                    filepath, encoded_string = capture(self.screen, self.output_dir)
                    self.last_frame_path=filepath
                    self.last_frame_base64 = encoded_string
                    self.game_frames.append(filepath)
                    
                    invalid_action_count_temp = 0
                    
                    frame_flag = False
                    
                    if done:
                        self.over = True
                else:
                    info = "Invalid action, which should be one of " + str(self.valid_actions)

                    invalid_action_count_temp += 1
                    self.invalid_action_count += 1
                    if invalid_action_count_temp == 3:
                        action = random.choices(self.valid_actions, k=1)[0]
                        invalid_action_count_temp = 0
                        done, info = self.step(action, dt)
                        # History
                        self.history_frame_base64 = self.last_frame_base64
                        self.history_action = action
                        self.history_action_info = info
                        self.history_valid_action = action
                        frame_flag = False
                        filepath, encoded_string = capture(self.screen, self.output_dir)
                        self.last_frame_path=filepath
                        self.last_frame_base64 = encoded_string
                        self.game_frames.append(filepath)
                        
                        if done:
                            self.over = True
                        # action = input("Please enter your action (left, right, up, down or quit): ").strip().lower()
                    else:
                        # History
                        self.history_action = action
                        self.history_action_info = info
                        self.history_frame_base64 = self.last_frame_base64
                        filepath, encoded_string = capture(self.screen, self.output_dir)
                        self.last_frame_path=filepath
                        self.last_frame_base64 = encoded_string
                        self.game_frames.append(filepath)
                        self.new_action_event.clear()  # 清除事件，准备接收下一个动作     
            else:
                waiting_time += 1
                if waiting_time > 2000 * 30:
                    # kill input thread
                    thread_event.set()
                    input_thread.join()
                    waiting_time = 0
                    
                    thread_event = threading.Event()
                    input_thread = threading.Thread(target=input_thread_method, args=(thread_event,), daemon=True)
                    input_thread.start()

        
        if not human_mode and input_thread.is_alive():
            thread_event.set()   # 通知输入线程退出
            input_thread.join()  # 等待输入线程退出    