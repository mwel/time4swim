import asyncio
import websockets
import json
import sqlite3
from datetime import datetime, timezone
import os

# Define the path to the SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), "../crowd.db")

def initialize_database():
    """Create the database table if it doesn't exist yet."""
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS crowdmonitor (
                timestamp TEXT NOT NULL,
                uid TEXT NOT NULL,
                current_fill INTEGER NOT NULL,
                max_space INTEGER NOT NULL
            )
        """)
        db.commit()

def save_entries(timestamp, entries):
    """Insert multiple entries into the database."""
    with sqlite3.connect(DB_PATH) as db:
        db.executemany("""
            INSERT INTO crowdmonitor (timestamp, uid, current_fill, max_space)
            VALUES (?, ?, ?, ?)
        """, [
            (timestamp, item["uid"], int(item["currentfill"]), int(item["maxspace"]))
            for item in entries
        ])
        db.commit()

async def fetch_crowd_data():
    """Connect to the WebSocket, fetch the data, and save it."""
    url = "wss://badi-public.crowdmonitor.ch:9591/api"
    async with websockets.connect(url) as websocket:
        await websocket.send("all")
        response = await websocket.recv()
        data = json.loads(response)
        timestamp = datetime.now(timezone.utc).isoformat()
        save_entries(timestamp, data)
        print(f"[{timestamp}] Stored {len(data)} entries.")

if __name__ == "__main__":
    initialize_database()
    asyncio.run(fetch_crowd_data())

