# Updated and Corrected Files

## data_preparation.py

import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Database path
DATABASE_PATH = "data/intraday_data.db"

# Load data from the database
def load_data(symbol):
    conn = sqlite3.connect(DATABASE_PATH)
    query = f"""
        SELECT symbol, datetime, close, ema_8, ema_21, ema_50, rsi_14, macd, macd_signal, doji, hammer, engulfing, vwap
        FROM intraday_data
        WHERE symbol = '{symbol}'
        ORDER BY datetime ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Ensure no missing values
    df.dropna(subset=["ema_8", "ema_21", "ema_50", "rsi_14", "macd", "macd_signal"], inplace=True)

    # Convert datetime to a usable format
    df["datetime"] = pd.to_datetime(df["datetime"])

    return df


# Prepare data for training
def prepare_data(df):
    required_columns = ["ema_8", "ema_21", "ema_50", "rsi_14", "macd", "macd_signal", "doji", "hammer", "engulfing", "vwap"]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in data: {missing_cols}")

    # Features and labels
    X = df[required_columns]
    y = df["close"].pct_change().apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0)  # Buy (1), Sell (-1), Hold (0)

    # Drop the first row (NaN from pct_change)
    X = X.iloc[1:]
    y = y.iloc[1:]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    # Normalize the features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test, scaler

# Save prepared data to CSV
def save_to_csv(df, filename="prepared_data.csv"):
    print(f"Saving data to {filename}...")
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}.")

if __name__ == "__main__":
    tickers_csv_path = "tickers.csv"
    tickers_df = pd.read_csv(tickers_csv_path)
    stock_symbols = tickers_df["Symbol"].dropna().tolist()

    all_data = []

    for symbol in stock_symbols:
        print(f"Loading data for {symbol}...")
        df = load_data(symbol)
        all_data.append(df)

    # Combine data for all stocks into one DataFrame
    combined_data = pd.concat(all_data, ignore_index=True)

    # Save the combined dataset to CSV
    save_to_csv(combined_data)

    print("Data preparation complete.")
