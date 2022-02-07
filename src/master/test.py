import requests
import json
import time
import threading
import asyncio
import websockets
from master import *

async def themain():
    new_ws = API_ENDPOINT+"/gateway?v=4"
    cws = requests.get(new_ws,headers={"authorization":f"{SLAVE_TOKEN}"}).json()["url"]
    async with websockets.connect(cws) as ws:
        interval = json.loads(await ws.recv())["d"]["heartbeat_interval"]
        print(interval)
        handshake = json.dumps({
            "op":2,
            "d":{"token":f"{SLAVE_TOKEN}","properties":{"$os":"win","$browser:":"disco","$device":"disco"}}
        })
        await ws.send(handshake)
        while True:
            data = json.loads(await ws.recv())
            if data["t"] == "READY":
                print(data["d"]["session_id"])


        '''''
        voice_conn = json.dumps({
            "op":4,
            "d":{
                "guild_id":"707412680096481320",
                "channel_id":"707412680096481324"
            }
            })
        await ws.send(voice_conn)
        #'''


asyncio.run(themain())
