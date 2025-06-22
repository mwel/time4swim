import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# === Set up database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "crowd.db")

# === Load data with pool name from JOIN
conn = sqlite3.connect(DB_PATH)
query = '''
    SELECT c.*, COALESCE(p.name, c.uid) AS name
    FROM crowdmonitor c
    LEFT JOIN pools p ON c.uid = p.uid
'''
df = pd.read_sql(query, conn, parse_dates=["timestamp"])
conn.close()

# === Timezone conversion
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert("Europe/Zurich")

# === Filter for one specific pool (e.g., Hallenbad City)
df = df[df["name"] == "Hallenbad City"]
df = df[df["timestamp"].dt.hour.between(6, 22)]

# === Extract weekday and hour
df["weekday"] = df["timestamp"].dt.day_name()
df["hour"] = df["timestamp"].dt.hour

# === Aggregate average visitors by weekday and hour
agg = df.groupby(["weekday", "hour"]).current_fill.mean().reset_index()

# === Build full time grid: all days and hours
weekdays_ordered = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
hours = list(range(6, 23))
full_grid = pd.MultiIndex.from_product([weekdays_ordered, hours], names=["weekday", "hour"]).to_frame(index=False)

# === Merge real data with full grid and fill missing values with 0
heatmap_df = pd.merge(full_grid, agg, how="left", on=["weekday", "hour"]).fillna(0)

# === Pivot to matrix format for heatmap
heatmap_data = heatmap_df.pivot(index="hour", columns="weekday", values="current_fill")
heatmap_data = heatmap_data[weekdays_ordered]  # ensure correct weekday order

# === Create mask for zero values (to gray out)
mask = heatmap_data == 0

# === Plot heatmap
sns.set_style("white")
plt.figure(figsize=(12, 6))
sns.heatmap(
    heatmap_data,
    cmap="coolwarm",
    mask=mask,
    linewidths=0.5,
    annot=True,
    fmt=".0f",
    cbar_kws={"label": "Avg. visitors"},
    square=False
)

plt.gca().set_facecolor("#eeeeee")
plt.title("Avg. visitors – Hallenbad City (by day and hour)")
plt.xlabel("Day of week")
plt.ylabel("Hour of day")
plt.tight_layout()
plt.show()