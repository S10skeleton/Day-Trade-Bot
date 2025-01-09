import sqlite3
import pandas as pd

# Path to the SQLite database
DATABASE_PATH = "data/intraday_data.db"

# Connect to the database
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Print the table schema to verify columns
cursor.execute("PRAGMA table_info(intraday_data)")
print(cursor.fetchall())

# Query the database to load data into a DataFrame
query = """
    SELECT *
    FROM intraday_data
    ORDER BY datetime ASC
"""
df = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Display the first few rows of the DataFrame
print(df.head())
