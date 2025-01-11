import gym
import numpy as np
from gym import spaces
import pandas as pd

class TradingEnvironment(gym.Env):
    def __init__(self, data, stocks, initial_balance=10000):
        super(TradingEnvironment, self).__init__()
        self.data = data
        self.stocks = stocks
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {stock: 0 for stock in stocks}
        self.total_value = self.balance
        self.current_step = 0
        self.done = False  # Initialize the 'done' flag

        # Observation space includes features for all stocks + balance
        obs_space_size = len(self.stocks) * 6 + 1  # Example: 6 features per stock + 1 for balance
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_space_size,), dtype=np.float32)

        # Action space allows Buy/Sell/Hold for each stock
        self.action_space = spaces.MultiDiscrete([3] * len(stocks))



    def reset(self):
        self.balance = self.initial_balance
        self.positions = {stock: 0 for stock in self.stocks}
        self.total_value = self.balance
        self.current_step = 0
        self.done = False  # Reset the 'done' flag
        obs = self._get_observation()
        print(f"Observation size after reset: {len(obs)}, Expected: {self.observation_space.shape[0]}")
        return obs




    def _get_observation(self):
        obs = []
        for stock in self.stocks:
            stock_data = self.data[self.data["symbol"] == stock]
            if self.current_step < len(stock_data):  # Check if data exists for the current step
                stock_row = stock_data.iloc[self.current_step]
                obs.extend(stock_row[["ema_8", "ema_21", "rsi_14", "macd", "macd_signal", "vwap"]].values)
            else:
                print(f"Skipping stock {stock} due to insufficient data at step {self.current_step}")
                obs.extend([0] * 6)  # Fill with zeros if no data is available for this stock
        obs.append(self.balance)  # Include the remaining balance
        obs = np.array(obs, dtype=np.float32)
        
        # Debugging print
        # print(f"Expected observation space size: {self.observation_space.shape[0]}")
        # print(f"Actual observation size: {len(obs)}")
        
        # Ensure the observation matches the defined space
        assert len(obs) == self.observation_space.shape[0], (
            f"Observation size mismatch: got {len(obs)}, expected {self.observation_space.shape[0]}"
        )
        return obs


    def step(self, actions):
        for i, stock in enumerate(self.stocks):
            action = actions[i]

            # Get current stock price
            stock_data = self.data[self.data["symbol"] == stock]
            if self.current_step < len(stock_data):
                current_price = stock_data.iloc[self.current_step]["close"]

                # Handle Buy, Sell, or Hold actions
                if action == 1:  # Buy
                    max_shares = self.balance // current_price
                    self.positions[stock] += max_shares
                    self.balance -= max_shares * current_price
                elif action == 2:  # Sell
                    self.balance += self.positions[stock] * current_price
                    self.positions[stock] = 0

        # Update portfolio value
        self.total_value = self.balance + sum(
            self.positions[stock] * self.data[self.data["symbol"] == stock].iloc[self.current_step]["close"]
            for stock in self.stocks if self.current_step < len(self.data[self.data["symbol"] == stock])
        )

        # Advance the step and check if the episode is done
        self.current_step += 1
        self.done = self.current_step >= len(self.data[self.data["symbol"] == self.stocks[0]]) - 1

        # Calculate reward
        reward = self.total_value - self.balance  # Reward based on portfolio value change
        obs = self._get_observation()

        return obs, reward, self.done, {}


    def render(self, mode="human"):
        print(
            f"Step: {self.current_step}, Balance: {self.balance}, "
            f"Position: {self.position}, Total Value: {self.total_value}"
        )
