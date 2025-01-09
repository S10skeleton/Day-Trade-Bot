import gym
import numpy as np
from gym import spaces
import pandas as pd

class TradingEnvironment(gym.Env):
    def __init__(self, data, initial_balance=10000):
        super(TradingEnvironment, self).__init__()

        self.data = data
        self.initial_balance = initial_balance

        # Define action and observation space
        self.action_space = spaces.Discrete(3)  # Hold, Buy, Sell
        num_features = self.data.shape[1] - 1  # Exclude 'datetime'
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(num_features + 2,), dtype=np.float32
        )  # +2 for cash and current position

        self.reset()

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0
        self.total_value = self.balance
        self.done = False
        return self._get_observation()

    def _get_observation(self):
        state = self.data.iloc[self.current_step].drop(labels=["datetime"]).values.astype(float)
        return np.append(state, [self.balance, self.position])



def step(self, action):
    if self.done:
        raise RuntimeError("Episode has ended. Call reset to start a new episode.")

    # Get current price
    current_price = self.data.iloc[self.current_step]["close"]

    # Apply action
    if action == 1:  # Buy
        max_shares = self.balance // current_price
        self.position += max_shares
        self.balance -= max_shares * current_price

    elif action == 2:  # Sell
        self.balance += self.position * current_price
        self.position = 0

    # Update portfolio value
    self.total_value = self.balance + self.position * current_price

    # Compute reward
    reward = self.total_value - self.initial_balance

    # Add penalties/rewards based on indicators
    if self.data.iloc[self.current_step]["doji"]:
        reward -= 5  # Penalize trading during doji
    if self.data.iloc[self.current_step]["hammer"]:
        reward += 5  # Reward trading on hammer signal
    if self.data.iloc[self.current_step]["engulfing"]:
        reward += 10  # Reward trading on engulfing signal
    if action == 1 and current_price < self.data.iloc[self.current_step]["vwap"]:
        reward += 10  # Reward buying below VWAP
    elif action == 2 and current_price > self.data.iloc[self.current_step]["vwap"]:
        reward += 10  # Reward selling above VWAP

    # Advance to the next step
    self.current_step += 1
    if self.current_step >= len(self.data) - 1:
        self.done = True

    # Get next state
    next_state = self._get_observation()

    return next_state, reward, self.done, {}


def render(self, mode="human"):
        print(
            f"Step: {self.current_step}, Balance: {self.balance}, "
            f"Position: {self.position}, Total Value: {self.total_value}"
        )
