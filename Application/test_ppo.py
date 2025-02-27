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

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TICKERS_FILE = os.path.join(BASE_DIR, "tickers.csv")
PREPARED_DATA_FILE = os.path.join(BASE_DIR, "prepared_data.csv")
MODEL_FILE = os.path.join(BASE_DIR, "ppo_day_trade_bot.zip")

# Load stock symbols from tickers.csv
def get_stock_symbols():
    if not os.path.exists(TICKERS_FILE):
        raise FileNotFoundError(f"{TICKERS_FILE} not found.")
    tickers_df = pd.read_csv(TICKERS_FILE)
    stock_symbols = tickers_df["Symbol"].dropna().tolist()
    if not stock_symbols:
        raise ValueError("No stock symbols found in tickers.csv.")
    return stock_symbols

# Load and filter prepared data
def load_data(stock_symbols):
    if not os.path.exists(PREPARED_DATA_FILE):
        raise FileNotFoundError(f"{PREPARED_DATA_FILE} not found.")
    data = pd.read_csv(PREPARED_DATA_FILE)
    data = data[data["symbol"].isin(stock_symbols)]
    if data.empty:
        raise ValueError("No data available for the stocks listed in tickers.csv.")
    return data

# Initialize and train the PPO model
def train_model(env):
    try:
        print("Starting train_model function...")
        
        # Check if the model file exists
        if os.path.exists(MODEL_FILE):
            print(f"Model file found at {MODEL_FILE}. Loading existing model...")
            model = PPO.load(MODEL_FILE, env=env)
        else:
            print(f"No saved model found at {MODEL_FILE}. Creating a new model...")
            model = PPO(
                "MlpPolicy",
                env,
                verbose=1,
                device="cpu",  # Use "cuda" if GPU is available
                learning_rate=0.0001,
                n_steps=4096,  # Increase rollout steps
                batch_size=256,  # Larger batch size
                gamma=0.99,
                tensorboard_log="./ppo_tensorboard/"
            )
            print("New model created successfully.")
        
        print("Starting training process...")
        
        # Train the model
        model.learn(total_timesteps=500, tb_log_name="PPO_run")
        print("Training process completed successfully.")
        
        # Save the trained model
        model.save(MODEL_FILE)
        print(f"Model saved successfully as {MODEL_FILE}.")
        
        return model
    
    except Exception as e:
        print(f"An error occurred in train_model: {str(e)}")
        raise


# Visualize and test the trained model
def test_model(env, model):
    buy_count = 0
    sell_count = 0
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

            # Write to text-based log
            log.write(f"{step},{action},{env.data.iloc[env.current_step]['close']},{env.total_value}\n")

            step += 1

            if done:
                break

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

# Main function
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true", help="Run training and testing")
    args = parser.parse_args()

    if args.train:
        try:
            stock_symbols = get_stock_symbols()
            data = load_data(stock_symbols)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")
            exit()

        env = TradingEnvironment(data, stocks=stock_symbols)
        model = train_model(env)
        test_model(env, model)
    else:
        print("No action specified. Use --train to start training.")

