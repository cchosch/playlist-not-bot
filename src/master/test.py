import requests
import json
import time
import threading
import asyncio
import websockets
from master import *
from heartbeat import *



async def main():
    new_ws = API_ENDPOINT+"/gateway?v=4"
    SEQUENCE_NUM = None
    SESSION_ID = None
    while True:
        cws = requests.get(new_ws,headers=MASTER_AUTH_HEADER).json()["url"]
        async with websockets.connect(cws) as ws:
            if SESSION_ID == None:
                await ws.send(json.dumps({
                    "op":2,
                    "d":{"token":f"Bot {MASTER_AUTH}","properties":{"$os":"win","$browser:":"disco","$device":"disco"}}
                }))
            interval = (json.loads(await ws.recv())["d"]["heartbeat_interval"])/1000
            MAIN_HEARTBEAT = Heartbeat(args=(ws, interval))
            MAIN_HEARTBEAT.start()
            while True:
                res = json.loads(await ws.recv())
                print(res)
                if res["t"] == "READY":
                    SESSION_ID = res["d"]["session_id"]
                if res["s"] != None:
                    SEQUENCE_NUM = res["s"]
                    MAIN_HEARTBEAT.snum = res["s"]
                if res["op"] == 9:
                    MAIN_HEARTBEAT.stop_exe()
            
print(json.dumps(requests.get(f"{API_ENDPOINT}/guilds/763224124612542504",headers={
    "Authorization":f"Bot {MASTER_AUTH}"
}).json(),indent=2))
#asyncio.run(main())


