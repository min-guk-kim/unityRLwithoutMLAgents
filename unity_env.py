"""
This Python script was written to demonstrate reinforcement learning in Unity without the use of ML-agents.

Written by Minguk Kim @ Texas A&M University
mingukkim@tamu.edu
"""
# libraries for reinforcement learning
from __future__ import annotations
import numpy as np
import gymnasium as gym
from gymnasium import spaces

# libraries for Python-Unity communication
from communication import UnityCommunication

### Registering pre-defined Unity env into local Gym.
from gymnasium.envs.registration import register

register(
    id='UnityEnv-v1',
    entry_point='unity_env:UnityEnv',
    max_episode_steps= 1_000
)


### Convert the Unity environment into a gym environment
class UnityEnv(gym.Env):
    """
    This class is an example unity environment for RL.
    
    Agent's Goal: reach the goal as soon as possible. 
    State: Agent Position (x,z) & Initial Position: (0,0)
    Action: Up, down, left, right (each action makes the agent move +1 to the desired direction)
    Reward: +1 When reached the goal (4,4)
    """

    def __init__(self):
        super(UnityEnv, self).__init__()
        
        # Initialize Unity communication
        self.unity_comm = UnityCommunication()
        
        # Initializes state and action spaces
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32)
        self.action_space = spaces.Discrete(4) # 0: up, 1: down, 2: left, 3: right
        
        # Initialize environment before the first episode.
        self.agent_pos = [0.0, 0.0]
        self.goal_pos = [4.0, 4.0]
        self.max_timesteps = 100
        self.current_timestep = 0
        self.np_random = None
        self.seed()
        # Variable to record rewards for each episode
        self.episode_rewards = []
        
    def step(self, action):
        """
        Update agent position based on action and send it to Unity via 
        TCP using the UnityCommunication instance
        """
        try:
            # Update agent position based on action and send it to Unity via TCP
            if action == 0:  # up
                self.agent_pos[1] += 1.0
            elif action == 1:  # down
                self.agent_pos[1] -= 1.0
            elif action == 2:  # left
                self.agent_pos[0] -= 1.0
            elif action == 3:  # right
                self.agent_pos[0] += 1.0

            # Clamp x and z within the range [0, 4]
            self.agent_pos[0] = max(0.0, min(4.0, self.agent_pos[0]))
            self.agent_pos[1] = max(0.0, min(4.0, self.agent_pos[1]))

            # Send updated position and receive agent's position from Unity
            self.agent_pos = self.unity_comm.send_position(self.agent_pos)

            # Formulate observation
            observation = np.array(self.agent_pos + self.goal_pos)

            # Reward calculation and episode termination conditions
            reward = 1.0 if (self.agent_pos[0] == self.goal_pos[0] and self.agent_pos[1] == self.goal_pos[1]) else 0.0
            self.episode_rewards.append(reward)
            self.current_timestep += 1

            terminated = reward == 1.0
            truncated = self.current_timestep >= self.max_timesteps

            return observation, reward, terminated, truncated, {}
        except BrokenPipeError:
            print("Connection lost while trying to send data. Closing the socket.")
            self.sock.close()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
    def seed(self, seed=None):
        self.np_random, seed = gym.utils.seeding.np_random(seed)
        return [seed]
    
    def reset(self, **kwargs):
        seed_value = kwargs.get('seed')
        if seed_value is not None:
            self.seed(seed_value)
        
        self.agent_pos = [0.0, 0.0]  # Reset position
        self.current_timestep = 0
        
        observation = np.array(self.agent_pos + self.goal_pos, dtype=np.float32)
        
        # Send reset command to Unity if necessary
        return observation, {}

    def render(self):
        # TODO: Later on, enables no-graphics mode for Unity Build File.
        pass
        
    def connect_and_check_unity(self):
        """
        Establish a connection to Unity.
        """
        return self.unity_comm.connect_and_check_unity()
            
    def send_message_training_over(self):
        """
        Send a message to Unity indicating the training is over.
        """
        self.unity_comm.send_message_training_over()
        
            
        