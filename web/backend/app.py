from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS
import os
import subprocess
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Paths
APPLICATION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../application'))
TICKERS_FILE = os.path.join(APPLICATION_DIR, 'tickers.csv')
TRADE_LOG = os.path.join(APPLICATION_DIR, 'trade_log.txt')

# Routes...

@app.route('/stocks', methods=['GET', 'POST', 'DELETE'])
def manage_stocks():
    """Manage stock tickers in tickers.csv."""
    if request.method == 'GET':
        try:
            with open(TICKERS_FILE, 'r') as f:
                stocks = f.read().splitlines()
            stocks = [stock for stock in stocks if stock.strip().lower() != "symbol"]
            return jsonify(stocks)
        except FileNotFoundError:
            return jsonify({"error": "tickers.csv not found"}), 404

    elif request.method == 'POST':
        symbol = request.json.get('symbol')
        if not symbol:
            return jsonify({"error": "No symbol provided"}), 400

        try:
            # Read existing lines and remove empty lines
            with open(TICKERS_FILE, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]

            # Add the new stock if it doesn't already exist
            if symbol in lines:
                return jsonify({"error": f"Stock {symbol} already exists."}), 400

            lines.append(symbol)

            # Write back to the file with proper formatting
            with open(TICKERS_FILE, 'w') as f:
                f.write('\n'.join(lines) + '\n')

            return jsonify({"message": f"Stock {symbol} added."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500




    elif request.method == 'DELETE':
        symbol = request.json.get('symbol')
        if not symbol:
            return jsonify({"error": "No symbol provided"}), 400

        try:
            with open(TICKERS_FILE, 'r') as f:
                stocks = f.read().splitlines()
            if symbol not in stocks:
                return jsonify({"error": f"Stock {symbol} not found"}), 404
            stocks.remove(symbol)
            with open(TICKERS_FILE, 'w') as f:
                f.write('\n'.join(stocks))
            return jsonify({"message": f"Stock {symbol} removed."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Trigger Training
@app.route('/train', methods=['POST'])
def train_model():
    """Trigger model training by running test_ppo.py."""
    try:
        result = subprocess.run(
            ["python", os.path.join(APPLICATION_DIR, "test_ppo.py")],
            check=True,
            capture_output=True,
            text=True
        )
        return jsonify({"message": "Training complete", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Training failed: {e.stderr}"}), 500

# Portfolio Data
@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Fetch portfolio data from trade_log.txt."""
    if not os.path.exists(TRADE_LOG):
        return jsonify({"error": "Portfolio data not available"}), 404

    try:
        df = pd.read_csv(TRADE_LOG)
        total_value = df["Portfolio Value"].iloc[-1]
        portfolio = {
            "total_value": total_value,
            "stocks": df.to_dict(orient="records")
        }
        return jsonify(portfolio)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/tensorboard', methods=['GET'])
def serve_tensorboard():
    """Serve TensorBoard iframe link."""
    tensorboard_url = "http://localhost:6006"  # Adjust if TensorBoard runs on a different host/port
    return jsonify({"url": tensorboard_url})


if __name__ == '__main__':
    app.run(debug=True)
