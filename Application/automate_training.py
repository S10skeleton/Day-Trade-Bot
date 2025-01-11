
# python automate_training.py

import os
import subprocess

# Step 1: Fetch new data
print("Fetching new data...")
subprocess.run(["python", "scripts/data_fetch.py"], check=True)

# Step 2: Prepare the dataset
print("Preparing dataset...")
subprocess.run(["python", "data_preparation.py"], check=True)

# Step 3: Continue training the model
print("Continuing model training...")
subprocess.run(["python", "test_ppo.py"], check=True)


