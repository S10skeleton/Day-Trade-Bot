import os
import logging
import subprocess
import threading
import uuid
import sys
from datetime import datetime

# Configure logging
log_file_path = os.path.join(os.path.dirname(__file__), "training_manager.log")
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Log streaming file
stream_log_file = os.path.join(os.path.dirname(__file__), "trade_log.txt")

import uuid  # For generating unique session IDs

active_trainings = []  # Global list to track active training sessions\
active_trainings_lock = threading.Lock()  # Lock for thread-safe access


def start_training(model_path, env_path):
    """Start training the model and log progress."""
    log_file_path = os.path.join(os.path.dirname(__file__), "training_manager.log")
    session_id = str(uuid.uuid4())  # Generate a unique session ID

    with active_trainings_lock:  # Thread-safe append
        active_trainings.append(session_id)

    try:
        logging.info(f"Starting training session {session_id}...")
        with open(log_file_path, "a") as log_file:
            log_file.write(f"Training session {session_id} initiated...\n")

            # Run the training subprocess
            process = subprocess.Popen(
                [
                    sys.executable,  # Use the current Python interpreter
                    os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Application")), "test_ppo.py"),
                    "--train"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                for line in process.stdout:
                    log_file.write(f"STDOUT: {line}\n")
                    log_file.flush()
                    logging.info(line.strip())

                for line in process.stderr:
                    log_file.write(f"STDERR: {line}\n")
                    log_file.flush()
                    logging.error(line.strip())

                process.wait(timeout=3600)  # Timeout set to 1 hour

                if process.returncode == 0:
                    log_file.write(f"Training session {session_id} completed successfully.\n")
                    logging.info(f"Training session {session_id} completed successfully.")
                else:
                    log_file.write(f"Training session {session_id} failed with exit code {process.returncode}.\n")
                    logging.error(f"Training session {session_id} failed with exit code {process.returncode}.")
            except subprocess.TimeoutExpired:
                process.terminate()
                logging.error(f"Training session {session_id} timed out.")
                log_file.write(f"Training session {session_id} timed out.\n")
    except Exception as e:
        error_msg = f"Error during training session {session_id}: {str(e)}"
        logging.error(error_msg)
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{error_msg}\n")
    finally:
        with active_trainings_lock:  # Thread-safe remove
            if session_id in active_trainings:
                active_trainings.remove(session_id)
                logging.info(f"Training session")


def gather_progress():
    """Add relevant information to the log for display."""
    try:
        # Example of progress logging
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(stream_log_file, "a") as stream_log:
            stream_log.write(f"{current_time} - Training progress monitored...\n")
        logging.info("Progress updates gathered.")
    except Exception as e:
        logging.error(f"Error gathering progress: {str(e)}")

def reset_logs():
    """Clear the trade log and reset streaming."""
    try:
        with open(stream_log_file, "w") as stream_log:
            stream_log.write(f"Log reset at {datetime.now()}.\n")
        logging.info("Log reset successfully.")
    except Exception as e:
        logging.error(f"Error resetting logs: {str(e)}")
