import asyncio
import websockets
import json
from datetime import datetime

async def main():
    uri = "wss://badi-public.crowdmonitor.ch:9591/api"
    async with websockets.connect(uri) as websocket:
        await websocket.send("all")   # Fragt alle Daten ab
        message = await websocket.recv()
        data = json.loads(message)

        timestamp = datetime.utcnow().isoformat()
        for entry in data:
            uid = entry["uid"]
            current = entry["currentfill"]
            maxspace = entry["maxspace"]
            print(f"[{timestamp}] {uid}: {current} von {maxspace}")

asyncio.run(main())