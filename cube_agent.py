from __future__ import annotations
from collections import defaultdict
import numpy as np
from tqdm import tqdm
import gymnasium as gym

class CubeAgent:
    """
    Cube Model Class
    """
    def __init__(
        self,
        env: gym.Env,
        learning_rate: float,
        initial_epsilon: float,
        epsilon_decay: float,
        final_epsilon: float,
        discount_factor: float = 0.95,
    ):
        
        """
        ~
        """
        # defaultdict --> 없는 key를 불러와도 밸류는 자동으로 0
        self.q_values = defaultdict(lambda: np.zeros(env.action_space.n))
        self.lr = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = initial_epsilon
        self.epsilon_decay = epsilon_decay
        self.final_epsilon = final_epsilon
        self.training_error = []
        self.env = env
        
    def get_action(self, obs: np.ndarray) -> int: # 이 함수는 int형을 return한다.
        """
        obs: 환경에서 얻어진 관찰값 (예: 플레이어의 위치와 목표의 위치)
        """
        
        # epsilon-greedy 전략을 사용한 행동 선택을 한다.
        # 0~1의 값 중 하나를 뽑아서, 
        # greater than epsilon, 액션 하나를 랜덤추출. less than epsilon, Q가 가장 큰 액션 추출
        # 즉 epsilon이 클수록, explore보다는 exploit.
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        else:
            obs_tuple = tuple(obs.tolist()) # convert numpy array to tuple
            return int(np.argmax(self.q_values[obs_tuple]))
        
    def update(
        self,
        obs: np.ndarray,
        action: int,
        reward: float,
        terminated: bool,
        next_obs: np.ndarray,
    ):
        obs_tuple = tuple(obs.tolist())
        next_obs_tuple = tuple(next_obs.tolist())
        """Updates the Q-value of an action."""
        # 다음 상태 s'에서의 행동 중, 가장 Q가 높은 행동에 대한 Q값
        future_q_value = (not terminated) * np.max(self.q_values[next_obs_tuple])
        # 1-step TD: r * gamma * Q(s',a') - Q(s,a)
        temporal_difference = (
            reward + self.discount_factor * future_q_value - self.q_values[obs_tuple][action]
        )
        
        self.q_values[obs_tuple][action] = (
            self.q_values[obs_tuple][action] + self.lr * temporal_difference
        )
        self.training_error.append(temporal_difference)
        
    # decay되감에 따라 exploit 대신 explore를 더 많이 함.
    def decay_epsilon(self):
        self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)