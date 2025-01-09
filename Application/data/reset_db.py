import sqlite3
import os

# Resolve database path dynamically
DB_FILE = os.path.join(os.path.dirname(__file__), "historical_data.db")
TABLE_NAME = "market_data"

# SQL schema for the new table
TABLE_SCHEMA = f"""
CREATE TABLE {TABLE_NAME} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    ma_50 REAL,  -- 50-day moving average
    ma_200 REAL, -- 200-day moving average
    rsi_14 REAL, -- RSI (14-period)
    macd REAL,   -- MACD
    signal REAL  -- MACD signal line
);
"""

def reset_table():
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Drop the table if it exists
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")

        # Create a new table
        cursor.execute(TABLE_SCHEMA)

        # Commit the changes
        conn.commit()
        print(f"Table '{TABLE_NAME}' has been reset successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    reset_table()
