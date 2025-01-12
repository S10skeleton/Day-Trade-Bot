from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import subprocess
import pandas as pd
import threading
import uuid
import time
from training_manager import (
    active_trainings,  # Import active training sessions
    start_training,
    gather_progress,
    reset_logs,
)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Paths
APPLICATION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Application"))
TICKERS_FILE = os.path.join(APPLICATION_DIR, "tickers.csv")
TRADE_LOG = os.path.join(os.path.dirname(__file__), "trade_log.txt")
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
MODEL_FILE = os.path.join(ROOT_DIR, "Application", "ppo_day_trade_bot.zip")
LOG_FILE = os.path.join(BACKEND_DIR, "trade_log.txt")


# Routes
@app.route("/stocks", methods=["GET", "POST", "DELETE"])
def manage_stocks():
    """Manage stock tickers in tickers.csv."""
    if request.method == "GET":
        try:
            with open(TICKERS_FILE, "r") as f:
                stocks = f.read().splitlines()
            stocks = [stock for stock in stocks if stock.strip().lower() != "symbol"]
            return jsonify(stocks)
        except FileNotFoundError:
            return jsonify({"error": "tickers.csv not found"}), 404

    elif request.method == "POST":
        symbol = request.json.get("symbol")
        if not symbol:
            return jsonify({"error": "No symbol provided"}), 400

        try:
            with open(TICKERS_FILE, "r") as f:
                lines = [line.strip() for line in f if line.strip()]

            if symbol in lines:
                return jsonify({"error": f"Stock {symbol} already exists."}), 400

            lines.append(symbol)

            with open(TICKERS_FILE, "w") as f:
                f.write("\n".join(lines) + "\n")

            return jsonify({"message": f"Stock {symbol} added."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == "DELETE":
        symbol = request.json.get("symbol")
        if not symbol:
            return jsonify({"error": "No symbol provided"}), 400

        try:
            with open(TICKERS_FILE, "r") as f:
                stocks = f.read().splitlines()

            if symbol not in stocks:
                return jsonify({"error": f"Stock {symbol} not found"}), 404

            stocks.remove(symbol)

            with open(TICKERS_FILE, "w") as f:
                f.write("\n".join(stocks))

            return jsonify({"message": f"Stock {symbol} removed."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/stream-logs", methods=["GET"])
def stream_logs():
    """Stream logs from the training_manager.log file."""
    log_file = os.path.join(os.path.dirname(__file__), "training_manager.log")

    def generate():
        with open(log_file, "r") as f:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield f"data: {line}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/train", methods=["POST"])
def train_model():
    """Trigger model training."""
    session_id = str(uuid.uuid4())
    if session_id in active_trainings:
        return jsonify({"error": "Training session already active"}), 400

    active_trainings.append(session_id)

    def train():
        try:
            subprocess.run(
                ["python", os.path.join(APPLICATION_DIR, "test_ppo.py"), "--train"],
                check=True,
                text=True,
            )
        except Exception as e:
            print(f"Error during training: {e}")
        finally:
            active_trainings.remove(session_id)

    threading.Thread(target=train, daemon=True).start()
    return jsonify({"message": "Training started", "session_id": session_id}), 200


@app.route("/training-status", methods=["GET"])
def training_status():
    """Return the current number of active training sessions."""
    return jsonify({"active_sessions": len(active_trainings), "sessions": active_trainings})


@app.route("/portfolio", methods=["GET"])
def get_portfolio():
    """Fetch portfolio data from trade_log.txt."""
    if not os.path.exists(TRADE_LOG):
        return jsonify({"error": "Portfolio data not available"}), 404

    try:
        df = pd.read_csv(TRADE_LOG)
        total_value = df["Portfolio Value"].iloc[-1]
        portfolio = {
            "total_value": total_value,
            "stocks": df.to_dict(orient="records"),
        }
        return jsonify(portfolio)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/start-training", methods=["POST"])
def start_training_endpoint():
    """Start a new training session."""
    try:
        start_training(MODEL_FILE, os.path.join(APPLICATION_DIR, "env_config.json"))
        return jsonify({"message": "Training started successfully."})
    except Exception as e:
        return jsonify({"error": f"Failed to start training: {str(e)}"}), 500


@app.route("/gather-progress", methods=["POST"])
def gather_progress_endpoint():
    """Trigger progress updates."""
    try:
        gather_progress()
        return jsonify({"message": "Progress updates logged successfully."})
    except Exception as e:
        return jsonify({"error": f"Failed to gather progress: {str(e)}"}), 500


@app.route("/reset-logs", methods=["POST"])
def reset_logs_endpoint():
    """Reset the log file."""
    try:
        reset_logs()
        return jsonify({"message": "Logs reset successfully."})
    except Exception as e:
        return jsonify({"error": f"Failed to reset logs: {str(e)}"}), 500


@app.route("/update-stock-data", methods=["POST"])
def update_stock_data():
    """Run data_fetch.py and data_preparation.py from their respective directories."""
    scripts_dir = os.path.join(APPLICATION_DIR, "scripts")

    try:
        subprocess.run(
            ["python", "data_fetch.py"],
            cwd=scripts_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["python", "data_preparation.py"],
            cwd=APPLICATION_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
        return jsonify({"message": "Stock data updated successfully."})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Failed to update stock data: {e.stderr}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)


    # @app.route('/action-logs', methods=['GET'])
# def get_action_logs():
#     """Fetch logs from actions_log.csv, converting from trade_log.txt if necessary."""
#     ACTION_LOG = os.path.join(APPLICATION_DIR, 'actions_log.csv')
#     TRADE_LOG = os.path.join(APPLICATION_DIR, 'trade_log.txt')

#     # Convert trade_log.txt to actions_log.csv if missing
#     if not os.path.exists(ACTION_LOG):
#         if os.path.exists(TRADE_LOG):
#             try:
#                 with open(TRADE_LOG, "r") as infile, open(ACTION_LOG, "w", newline="") as outfile:
#                     reader = pd.read_csv(infile)
#                     writer = pd.DataFrame(reader)
#                     writer.to_csv(outfile, index=False)
#             except Exception as e:
#                 return jsonify({"error": f"Failed to convert trade_log.txt to actions_log.csv: {e}"}), 500
#         else:
#             return jsonify([])  # No logs available

#     # Read and return the actions_log.csv
#     try:
#         logs = []
#         with open(ACTION_LOG, "r") as file:
#             reader = csv.DictReader(file)
#             for row in reader:
#                 logs.append({
#                     "timestamp": row.get("Step", ""),
#                     "action": row.get("Action", ""),
#                     "price": float(row.get("Price", 0)),
#                     "value": float(row.get("Portfolio Value", 0)),
#                 })
#         return jsonify(logs)
#     except Exception as e:
#         return jsonify({"error": f"Error reading actions_log.csv: {e}"}), 500




