import os
import sqlite3
import pandas as pd
import requests
from datetime import datetime
from time import sleep
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Alpha Vantage API configuration
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TICKERS_CSV = os.path.join(BASE_DIR, '..', 'tickers.csv')
DATABASE_PATH = os.path.join(BASE_DIR, '..', 'data', 'intraday_data.db')

# Ensure the database has the appropriate table
def ensure_table_exists():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intraday_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            datetime TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            ema_8 REAL,
            ema_21 REAL,
            ema_50 REAL,
            rsi_14 REAL,
            macd REAL,
            macd_signal REAL,
            doji INTEGER,
            hammer INTEGER,
            engulfing INTEGER,
            vwap REAL,
            UNIQUE(symbol, datetime)
        )
    """)
    conn.commit()
    conn.close()

# Fetch intraday data for a specific symbol
def fetch_intraday_data(symbol, interval="1min"):
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": ALPHA_VANTAGE_API_KEY,
        "outputsize": "full"
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch data for {symbol}: {response.status_code}")
        return None

    data = response.json()
    if "Time Series (1min)" not in data:
        print(f"No intraday data found for {symbol}. Full response: {data}")
        return None

    return data["Time Series (1min)"]

# Save data to the database
def save_to_database(symbol, intraday_data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    for datetime_str, values in intraday_data.items():
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO intraday_data (symbol, datetime, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                datetime_str,
                float(values["1. open"]),
                float(values["2. high"]),
                float(values["3. low"]),
                float(values["4. close"]),
                int(values["5. volume"])
            ))
        except Exception as e:
            print(f"Error saving data for {symbol} at {datetime_str}: {e}")

    conn.commit()
    conn.close()

# Update intraday data for multiple symbols
def update_intraday_data():
    ensure_table_exists()

    if not os.path.exists(TICKERS_CSV):
        print(f"ERROR: {TICKERS_CSV} does not exist.")
        return

    # Read symbols from tickers.csv
    tickers_df = pd.read_csv(TICKERS_CSV)
    symbols = tickers_df["Symbol"].dropna().tolist()

    if not symbols:
        print("No symbols found in tickers.csv.")
        return

    for symbol in symbols:
        print(f"Fetching intraday data for {symbol}...")
        intraday_data = fetch_intraday_data(symbol)
        if intraday_data:
            save_to_database(symbol, intraday_data)
        else:
            print(f"Skipping {symbol} due to API data issue.")
        sleep(15)  # To avoid hitting API rate limits

if __name__ == "__main__":
    update_intraday_data()
