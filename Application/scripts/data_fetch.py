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
            UNIQUE(symbol, datetime)
        )
    """)

    # Ensure required columns for indicators exist
    columns = {
        "ema_8": "REAL",
        "ema_21": "REAL",
        "ema_50": "REAL",
        "rsi_14": "REAL",
        "macd": "REAL",
        "macd_signal": "REAL",
        "doji": "INTEGER",
        "hammer": "INTEGER",
        "engulfing": "INTEGER",
        "vwap": "REAL",
    }

    for column, column_type in columns.items():
        try:
            cursor.execute(f"ALTER TABLE intraday_data ADD COLUMN {column} {column_type}")
        except sqlite3.OperationalError:
            pass  # Column already exists

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

    conn.commit()
    conn.close()

# Compute indicators for a specific symbol
def compute_indicators(symbol):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    df = pd.read_sql_query(f"""
        SELECT * FROM intraday_data WHERE symbol = '{symbol}' ORDER BY datetime ASC
    """, conn)

    if df.empty:
        print(f"No data available for {symbol} to compute indicators.")
        conn.close()
        return

    # Ensure proper data types
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['open'] = pd.to_numeric(df['open'], errors='coerce')
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['low'] = pd.to_numeric(df['low'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    df.dropna(inplace=True)

    # Compute EMAs
    df['ema_8'] = df['close'].ewm(span=8, adjust=False).mean()
    df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()

    # Compute RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    rs = gain / loss
    df['rsi_14'] = 100 - (100 / (1 + rs))

    # Compute MACD
    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema_12 - ema_26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    # Compute candlestick patterns
    df = compute_candlestick_patterns(df)

    # Compute VWAP
    df = compute_vwap(df)

    print("Indicators computed for:", symbol)
    print(df[["datetime", "ema_8", "ema_21", "ema_50", "rsi_14", "macd", "macd_signal", "doji", "hammer", "engulfing", "vwap"]].head())

    # Update database
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                UPDATE intraday_data
                SET ema_8 = ?, ema_21 = ?, ema_50 = ?, rsi_14 = ?, macd = ?, macd_signal = ?, doji = ?, hammer = ?, engulfing = ?, vwap = ?
                WHERE symbol = ? AND datetime = ?
            """, (
                row['ema_8'], row['ema_21'], row['ema_50'], row['rsi_14'], row['macd'], row['macd_signal'],
                int(row['doji']), int(row['hammer']), int(row['engulfing']), row['vwap'],
                symbol, row['datetime']
            ))
        except Exception as e:
            print(f"Error updating {symbol} at {row['datetime']}: {e}")

    conn.commit()
    conn.close()


def compute_candlestick_patterns(df):
    df['doji'] = (abs(df['open'] - df['close']) / (df['high'] - df['low'])) < 0.1
    df['hammer'] = ((df['high'] - df['low']) > 2 * abs(df['open'] - df['close'])) & \
                   ((df['close'] - df['low']) / (.001 + df['high'] - df['low']) > 0.6) & \
                   ((df['open'] - df['low']) / (.001 + df['high'] - df['low']) > 0.6)
    df['engulfing'] = ((df['close'] > df['open']) & (df['close'].shift(1) < df['open'].shift(1)) & \
                       (df['close'] > df['open'].shift(1)) & (df['open'] < df['close'].shift(1))) | \
                      ((df['close'] < df['open']) & (df['close'].shift(1) > df['open'].shift(1)) & \
                       (df['close'] < df['open'].shift(1)) & (df['open'] > df['close'].shift(1)))
    return df

def compute_vwap(df):
    df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    return df

# Update intraday data for multiple symbols
def update_intraday_data():
    ensure_table_exists()

    if not os.path.exists(TICKERS_CSV):
        print(f"ERROR: {TICKERS_CSV} does not exist.")
        return

    # Read symbols from tickers.csv
    tickers_df = pd.read_csv(TICKERS_CSV)
    symbols = tickers_df["Symbol"].dropna().tolist()

    for symbol in symbols:
        print(f"Fetching intraday data for {symbol}...")
        intraday_data = fetch_intraday_data(symbol)
        if intraday_data:
            save_to_database(symbol, intraday_data)
            compute_indicators(symbol)  # Compute indicators after fetching data
        sleep(15)  # To avoid hitting API rate limits

if __name__ == "__main__":
    update_intraday_data()
