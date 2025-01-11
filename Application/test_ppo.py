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

# Load stock symbols from tickers.csv
tickers_csv_path = os.path.join(os.path.dirname(__file__), "tickers.csv")
tickers_df = pd.read_csv(tickers_csv_path)
stock_symbols = tickers_df["Symbol"].dropna().tolist()

if not stock_symbols:
    raise ValueError("No stock symbols found in tickers.csv.")

# Load prepared data
data = pd.read_csv("prepared_data.csv")

# Filter data for the stocks listed in tickers.csv
data = data[data["symbol"].isin(stock_symbols)]

if data.empty:
    raise ValueError("No data available for the stocks listed in tickers.csv.")

# Create the custom trading environment
env = TradingEnvironment(data, stocks=stock_symbols)

# Check if a saved model exists
if os.path.exists("ppo_day_trade_bot.zip"):
    print("Loading existing model...")
    model = PPO.load("ppo_day_trade_bot", env=env)
else:
    print("No saved model found. Creating a new model...")
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        device="cuda",  # Force GPU usage
        learning_rate=0.0001,
        n_steps=2048,
        gamma=0.99,
        tensorboard_log="./ppo_tensorboard/"
    )

# Train PPO
model.learn(total_timesteps=100000)
model.save("ppo_day_trade_bot")
print("Model saved as ppo_day_trade_bot.zip")

# Testing phase and visualization (unchanged)


# Testing Phase
# Initialize counters for Buy and Sell actions
buy_count = 0
sell_count = 0

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

        # Increment counters for Buy (1) and Sell (2) actions
        for i, stock_action in enumerate(action):  # Iterate through actions for each stock
            if stock_action == 1:
                buy_count += 1
            elif stock_action == 2:
                sell_count += 1


        # Log data
        portfolio_values.append(env.total_value)
        prices.append(env.data.iloc[env.current_step]["close"])
        steps.append(step)

        # Debugging
        print(f"Step: {step}, Actions: {action}, Buy Count: {buy_count}, Sell Count: {sell_count}")

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
print(f"Total Buy actions: {buy_count}")
print(f"Total Sell actions: {sell_count}")

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

