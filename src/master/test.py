import requests
import json
import time
import threading
import asyncio
import websockets
from master import *

async def themain():
    new_ws = API_ENDPOINT+"/gateway"
    cws = requests.get(new_ws,headers={"authorization":f"{SLAVE_TOKEN}"}).json()["url"]
    async with websockets.connect(cws) as ws:
        while True:
            data = json.loads(await ws.recv())
            print(data)

asyncio.run(themain())
