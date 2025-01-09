import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from stable_baselines3 import PPO
from scripts.trading_env import TradingEnvironment
import pandas as pd
import matplotlib.pyplot as plt

# Load prepared data
data = pd.read_csv("prepared_data.csv")

# Create the custom trading environment
env = TradingEnvironment(data)

# Initialize PPO with optimized hyperparameters
model = PPO(
    "MlpPolicy",
    env,
    verbose=1,           # Display training progress
    learning_rate=0.0001, # Fine-grained learning
    n_steps=2048,         # Smaller batch size for quicker updates
    gamma=0.99,           # Balance short-term and long-term rewards
    tensorboard_log="./ppo_tensorboard/"  # Enable logging for TensorBoard
)

# Train PPO
model.learn(total_timesteps=100000)  # Increased timesteps for better training

# Testing Phase
portfolio_values = []
steps = []

obs = env.reset()
step = 0

while True:
    action, _states = model.predict(obs)
    obs, reward, done, info = env.step(action)

    portfolio_values.append(env.total_value)
    steps.append(step)

    step += 1

    if done:
        break

env.render()

# Plot portfolio value over time
plt.figure(figsize=(10, 6))
plt.plot(steps, portfolio_values, label="Portfolio Value", color="blue")
plt.title("Portfolio Value Over Time")
plt.xlabel("Steps")
plt.ylabel("Total Value")
plt.legend()
plt.grid()
plt.show()
