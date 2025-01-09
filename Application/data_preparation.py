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
        SELECT datetime, close, ema_8, ema_21, ema_50, rsi_14, macd, macd_signal
        FROM intraday_data
        WHERE symbol = '{symbol}'
        ORDER BY datetime ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Ensure no missing values
    df.dropna(inplace=True)

    # Convert datetime to a usable format (optional)
    df["datetime"] = pd.to_datetime(df["datetime"])

    return df

# Prepare data for training
def prepare_data(df):
    # Features and labels
    X = df[["ema_8", "ema_21", "ema_50", "rsi_14", "macd", "macd_signal", "doji", "hammer", "engulfing", "vwap"]]
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
    symbol = "MSFT"  # Example symbol
    print(f"Loading data for {symbol}...")
    df = load_data(symbol)

    # Save the raw data with indicators for inspection or use
    save_to_csv(df)

    print("Preparing data for training...")
    X_train, X_test, y_train, y_test, scaler = prepare_data(df)
    print("Data preparation complete.")
