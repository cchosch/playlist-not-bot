import random
import threading
import asyncio
import requests
import websockets
import time
import json
import bot
from heartbeat import *

epoch_tracker = {}
MAIN_HEARTBEAT = None
API_ENDPOINT = 'https://discord.com/api/v9'
def read_config():
    myconfig = open("config.json")
    re = json.load(myconfig)
    myconfig.close()
    clientid = requests.get(API_ENDPOINT+"/users/@me", headers={"Authorization":f"Bot "+ re["master_auth"]})
    clientid = clientid.json()["id"]
    userid = "" 
    try: userid = requests.get(API_ENDPOINT+"/users/@me",headers={"Authorization": re["slave_auth"]+""}).json()["id"]
    except KeyError: pass
    return re["master_auth"], clientid, re["master_client_secret"], re["master_redirect_uri"], re["slave_auth"], re["prefix"], userid

MASTER_AUTH, MASTER_CLIENT_ID, MASTER_CLIENT_SECRET, MASTER_REDIRECT_URI, SLAVE_TOKEN, PREFIX, SLAVE_ID = read_config()

MASTER_AUTH_HEADER = {
    "Authorization":f"Bot {MASTER_AUTH}"
}

def updateVariables():
    MASTER_AUTH, MASTER_CLIENT_ID, MASTER_CLIENT_SECRET, MASTER_REDIRECT_URI, SLAVE_TOKEN, PREFIX, SLAVE_ID = read_config()

def get_ratelimits(headers):
    return float(headers["x-ratelimit-reset"]), float(headers["x-ratelimit-remaining"])

def sr(res):
    '''
    make sure connection has not been terminated with the websocket server and if so reconnect to websocket
    '''
    if res["op"] == 9:
        return False
    return res

def heartbeat(thesocket, interval):
    time.sleep(interval*random.uniform(0.0,1.0))
    print("SENDING...")
    asyncio.run(thesocket.send(json.dumps({"op":1})))
    last = time.time()
    while not stop_heartbeat:
        if time.time()-last > interval:
            last = time.time()

async def main():
    guilds_url = API_ENDPOINT+"/users/@me/guilds"
    guilds_responce = requests.get(guilds_url,headers=MASTER_AUTH_HEADER)
    new_ws = API_ENDPOINT+"/gateway?v=4"
    SEQUENCE_NUM = None
    SESSION_ID = None
    for guild in guilds_responce.json():
        time.sleep(0.3)
        bot.add_slave_to_guild(guild["id"])
    while True:
        cws = requests.get(new_ws,headers=MASTER_AUTH_HEADER).json()["url"]
        async with websockets.connect(cws) as ws:
            interval = (json.loads(await ws.recv())["d"]["heartbeat_interval"])/1000
            MAIN_HEARTBEAT = Heartbeat(args=(ws, interval))
            MAIN_HEARTBEAT.start()
            if SESSION_ID == None:
                await ws.send(json.dumps({
                    "op":2,
                    "d":{"token":f"Bot {MASTER_AUTH}","properties":{"$os":"win","$browser:":"disco","$device":"disco"}}
                }))
            else:
                print(MASTER_AUTH,SESSION_ID,SEQUENCE_NUM)
                await ws.send(json.dumps({
                    "op":6,
                    "d":{
                        "token":f"Bot {MASTER_AUTH}",
                        "session_id":f"{SESSION_ID}",
                        "seq":f"{SEQUENCE_NUM}"
                    }
                }))
            while True:
                res = json.loads(await ws.recv())
                print(res)
                if res["op"] == 9:
                    MAIN_HEARTBEAT.stop
                    break
                if res["op"] != 11:
                    SEQUENCE_NUM = res["s"]
                    MAIN_HEARTBEAT.snum = res["s"] 
                if res["op"] == 0:
                    if res["t"] == "READY":
                        SESSION_ID = res["d"]["session_id"]
                        continue
                    if res["t"] == "MESSAGE_CREATE":
                        pass


if __name__ == "__main__":
    asyncio.run(main())
