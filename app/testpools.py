import os
import sqlite3
import pandas as pd

# Get absolute path to crowd.db (one level up)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "crowd.db")

# Connect and query
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM pools ORDER BY uid", conn)
conn.close()

# Print results
print(df.to_string(index=False))