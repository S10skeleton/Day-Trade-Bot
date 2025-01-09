# Day-Trade-Bot# Day-Trade-Bot

## Overview
Day-Trade-Bot is an AI-driven stock trading bot designed for day trading in financial markets. Leveraging advanced machine learning algorithms and technical indicators, the bot automates decision-making for buying, selling, or holding stocks. Initially focused on paper trading for testing and optimization, the bot is designed to integrate with real-time broker APIs for live trading.

---

## Features
- **Technical Indicators**: Computes and utilizes EMA (8, 21, 50), RSI, MACD, VWAP, and candlestick patterns (Doji, Hammer, Engulfing) for trading decisions.
- **AI Model**: Trained using Proximal Policy Optimization (PPO) for reinforcement learning.
- **Paper Trading**: Simulates trading using historical data for testing and optimization.
- **Real-Time Trading**: Planned integration with broker APIs for live trading (e.g., Alpaca, Interactive Brokers).
- **Visualization**: Provides graphical and text-based logs of portfolio performance and actions.
- **Customizable**: Fully customizable indicators, reward functions, and trading logic.

---

## File Structure
application/ ├── scripts/ │ ├── data_fetch.py # Fetches intraday stock data and computes indicators. │ ├── data_preparation.py # Prepares data for training by cleaning and formatting. │ ├── trading_env.py # Custom trading environment for AI training and testing. ├── test_ppo.py # Main script for training and testing the AI model. ├── test.py # Script for verifying database and computed indicators. ├── prepared_data.csv # Prepared dataset for AI model training. ├── README.md # Project documentation.

yaml
Copy code

---

## Setup

### Prerequisites
1. **Python Environment**:
   - Python 3.8 or higher.
   - Install required libraries:
     ```bash
     pip install -r requirements.txt
     ```
2. **API Key for Stock Data**:
   - Obtain an API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key) or another provider.

3. **Broker API** (for future live trading):
   - Obtain credentials from your preferred broker (e.g., Alpaca, Interactive Brokers).

### Environment Variables
Create a `.env` file in the root directory with the following keys:
ALPHA_VANTAGE_API_KEY=your_api_key_here

yaml
Copy code

---

## Usage

### Step 1: Fetch Stock Data
Run `data_fetch.py` to download intraday data and compute indicators:

python scripts/data_fetch.py
### Step 2: Prepare Data
Clean and prepare the fetched data for training:

python scripts/data_preparation.py
### Step 3: Train and Test the Model
Train the PPO model and simulate trading:

python test_ppo.py

### Step 4: Verify Data
Ensure indicators are computed and available:

python test.py


## Planned Features
Real-Time Integration:
Connect to broker APIs for live trading execution.
Strategy Refinement:
Incorporate additional indicators and AI models.
Performance Metrics:
Detailed metrics and backtesting results.

## Contributions
Contributions are welcome! Fork the repository, create a feature branch, and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

