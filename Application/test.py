import sqlite3
import pandas as pd

DATABASE_PATH = "data/intraday_data.db"

conn = sqlite3.connect(DATABASE_PATH)
df = pd.read_sql_query("SELECT * FROM intraday_data LIMIT 5", conn)
conn.close()

print(df.head())
