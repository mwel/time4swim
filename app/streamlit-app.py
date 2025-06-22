import os
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# === Database path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "crowd.db")

# === Load data with pool name via LEFT JOIN
conn = sqlite3.connect(DB_PATH)
query = '''
    SELECT c.*, p.name
    FROM crowdmonitor c
    JOIN pools p ON c.uid = p.uid
    WHERE p.name IS NOT NULL
'''
df = pd.read_sql(query, conn, parse_dates=["timestamp"])
conn.close()

# === Timezone conversion
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert("Europe/Zurich")

# === Filter by time (6 to 22)
df = df[df["timestamp"].dt.hour.between(6, 22)]

# === Streamlit UI
st.title("Pool Heatmap Viewer")

available_pools = sorted(df["name"].unique())
selected_pool = st.selectbox("Choose a pool", options=available_pools)

# === Filter for selected pool
df_pool = df[df["name"] == selected_pool]

if df_pool.empty:
    st.warning("No data available for this pool yet.")
else:
    # === Add time dimensions
    df_pool["weekday"] = df_pool["timestamp"].dt.day_name()
    df_pool["hour"] = df_pool["timestamp"].dt.hour

    # === Aggregate
    agg = df_pool.groupby(["weekday", "hour"]).current_fill.mean().reset_index()

    # === Time grid for completeness
    weekdays_ordered = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hours = list(range(6, 23))
    full_grid = pd.MultiIndex.from_product([weekdays_ordered, hours], names=["weekday", "hour"]).to_frame(index=False)

    heatmap_df = pd.merge(full_grid, agg, how="left", on=["weekday", "hour"]).fillna(0)
    heatmap_data = heatmap_df.pivot(index="hour", columns="weekday", values="current_fill")
    heatmap_data = heatmap_data[weekdays_ordered]

    # === Plot
    mask = heatmap_data == 0
    sns.set_style("white")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(
        heatmap_data,
        cmap="coolwarm",
        mask=mask,
        linewidths=0.5,
        annot=True,
        fmt=".0f",
        cbar_kws={"label": "Avg. visitors"},
        square=False,
        ax=ax
    )

    ax.set_facecolor("#eeeeee")
    ax.set_title(f"Avg. visitors – {selected_pool} (by day and hour)")
    ax.set_xlabel("Day of week")
    ax.set_ylabel("Hour of day")
    st.pyplot(fig)