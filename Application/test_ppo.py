import os
import sys
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Add the scripts directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))

from trading_env import TradingEnvironment
from stable_baselines3 import PPO
import pandas as pd
import matplotlib.pyplot as plt
import csv

# Load prepared data
data = pd.read_csv("prepared_data.csv")

# Ensure required columns exist
required_columns = ["ema_8", "ema_21", "ema_50", "rsi_14", "macd", "macd_signal", "doji", "hammer", "engulfing", "vwap", "close"]
missing_cols = [col for col in required_columns if col not in data.columns]
if missing_cols:
    raise ValueError(f"Missing required columns in prepared_data.csv: {missing_cols}")

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
actions = []  # Log actions
prices = []  # Log prices

obs = env.reset()
step = 0

# Create a text-based log for actions
with open("trade_log.txt", "w") as log:
    log.write("Step,Action,Price,Portfolio Value\n")  # Header row

    while True:
        action, _states = model.predict(obs)
        obs, reward, done, info = env.step(action)

        # Log data
        actions.append(action)
        portfolio_values.append(env.total_value)
        prices.append(env.data.iloc[env.current_step]["close"])
        steps.append(step)

        # Write to text-based log
        log.write(f"{step},{action},{env.data.iloc[env.current_step]['close']},{env.total_value}\n")

        step += 1

        if done:
            break

env.render()

# Save actions to a CSV for analysis
with open("actions_log.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Step", "Action", "Price", "Portfolio Value"])
    writer.writerows(zip(steps, actions, prices, portfolio_values))

# Calculate real-world time
interval_minutes = 1  # Update this if your data uses a different interval (e.g., 5 for "5min")
total_steps = len(steps)
real_world_minutes = interval_minutes * total_steps
real_world_hours = real_world_minutes / 60
real_world_days = real_world_hours / 24

print(f"\nReal-world time for the simulation: {real_world_minutes} minutes")
print(f"Equivalent to {real_world_hours:.2f} hours or {real_world_days:.2f} days\n")

# Plot portfolio value and actions
plt.figure(figsize=(12, 6))
plt.plot(steps, portfolio_values, label="Portfolio Value", color="blue")
plt.scatter(steps, prices, c=actions, cmap="cool", label="Actions (0=Hold, 1=Buy, 2=Sell)", alpha=0.5)
plt.title("Portfolio Value and Model Actions")
plt.xlabel("Steps")
plt.ylabel("Portfolio Value")
plt.legend()
plt.grid()
plt.show()
