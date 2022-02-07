import threading
import asyncio
import requests
import websockets
import time
import json
import bot

epoch_tracker = {}
stop_heartbeat = False
MAIN_HEARTBEAT = None
API_ENDPOINT = 'https://discord.com/api/v9'
SESSION_ID = None
def read_config():
    myconfig = open("config.json")
    re = json.load(myconfig)
    myconfig.close()
    clientid = requests.get(API_ENDPOINT+"/users/@me", headers={"Authorization":f"Bot "+ re["master_auth"]})
    clientid = clientid.json()["id"]
    userid = requests.get(API_ENDPOINT+"/users/@me",headers={"Authorization": re["slave_auth"]+""}).json()["id"]
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
    last = time.time()-30
    while not stop_heartbeat:
        if time.time()-last > interval-0.5:
            thesocket.send(json.dumps({"op":1}))
            last = time.time()

async def main():
    guilds_url = API_ENDPOINT+"/users/@me/guilds"
    guilds_responce = requests.get(guilds_url,headers=MASTER_AUTH_HEADER)
    new_ws = API_ENDPOINT+"/gateway?v=4"
    for guild in guilds_responce.json():
        time.sleep(0.3)
        bot.read_guild_messages(guild["id"])
    while True:
        cws = requests.get(new_ws,headers=MASTER_AUTH_HEADER).json()["url"]
        async with websockets.connect(cws) as ws:
            interval = (json.loads(await ws.recv())["d"]["heartbeat_interval"])/1000
            stop_heartbeat = False
            MAIN_HEARTBEAT = threading.Thread(target=heartbeat, args=(ws, interval))
            last = time.time()
            if SESSION_ID == None:
                handshake = json.dumps({
                    "op":2,
                    "d":{"token":f"{SLAVE_TOKEN}","properties":{"$os":"win","$browser:":"disco","$device":"disco"}}
                })
                await ws.send(handshake)
            else:
                pass
            while True:
                res = sr(json.loads(await ws.recv()))
                if res == False:
                    stop_heartbeat = True
                    break
                if res["op"] == 0:
                    print(res)
                    if res["t"] == "READY":
                        SESSION_ID = res["d"]["session_id"]
                        continue
                print(res)



if __name__ == "__main__":
    asyncio.run(main())
