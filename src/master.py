import random
import threading
import asyncio
import requests
import websockets
import time
import json
from bot import *
from heartbeat import *



voice_states = {} # voice states
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

async def main():
    slave_b = Bot()
    threading.Thread(target=slave_b.start_loop).start()
    guilds_url = API_ENDPOINT+"/users/@me/guilds"
    guilds_responce = requests.get(guilds_url,headers=MASTER_AUTH_HEADER)
    new_ws = API_ENDPOINT+"/gateway?v=4"
    SEQUENCE_NUM = None
    SESSION_ID = None
    for guild in guilds_responce.json():
        time.sleep(0.3)
        add_slave_to_guild(guild["id"])
    while True:
        print("connecting to websocket...")
        cws = requests.get(new_ws,headers=MASTER_AUTH_HEADER).json()["url"]
        async with websockets.connect(cws) as ws:
            if SESSION_ID != None:
                await ws.send(json.dumps({
                    "op": 6,
                    "d": {
                        "token": f"Bot {MASTER_AUTH}",
                        "session_id": SESSION_ID,
                        "seq": SEQUENCE_NUM
                    }
                }))
                print("DEBUG DATA")
                print(f"TOKEN: {MASTER_AUTH}, {type(MASTER_AUTH)}")
                print(f"SESSION_ID: {SESSION_ID}, {type(SESSION_ID)}")
                print(f"SEQUENCE NUMBER: {SEQUENCE_NUM}, {type(SEQUENCE_NUM)}")
            else:
                await ws.send(json.dumps({
                    "op":2,
                    "d":{"token":f"Bot {MASTER_AUTH}","properties":{"$os":"win","$browser:":"disco","$device":"disco"}}
                }))
            interval = (json.loads(await ws.recv())["d"]["heartbeat_interval"])/1000
            MAIN_HEARTBEAT = Heartbeat(args=(ws, interval))
            MAIN_HEARTBEAT.start()
            print("connected")
            while True:
                res = json.loads(await ws.recv())
                #print("MASTER\n"+json.dumps(res,indent=2))
                if res["s"] != None:
                    SEQUENCE_NUM = res["s"]
                    MAIN_HEARTBEAT.snum = res["s"] 
                if res["op"] == 9:
                    print("MASTER RECEIVED OP CODE 9")
                    MAIN_HEARTBEAT.stop_exe()
                    break
                if res["op"] == 0:
                    if res["t"] == "READY":
                        SESSION_ID = res["d"]["session_id"]
                        continue
                    if res["t"] == "VOICE_STATE_UPDATE":
                        voice_states[res["d"]["user_id"]] = res["d"]
                    if res["t"] == "GUILD_CREATE":
                        if res["d"]["voice_states"] != []:
                            for s in res["d"]["voice_states"]:
                                s["guild_id"] = res["d"]["id"]
                                s["member"] = requests.get(API_ENDPOINT+"/guilds/"+res["d"]["id"]+"/members/"+s["user_id"],headers=MASTER_AUTH_HEADER).json()
                                voice_states[s["user_id"]] = s
                    if res["t"] == "MESSAGE_CREATE":
                        if res["d"]["content"][0] == PREFIX: # if it is a command
                            args = res["d"]["content"].split(" ")
                            if args[0] == f"{PREFIX}":
                                if res["d"]["author"]["id"] in voice_states.keys(): # 
                                    userid = res["d"]["author"]["id"]
                                    if voice_states[userid]["channel_id"] != None: # in voice channel
                                        pass

if __name__ == "__main__":
    asyncio.run(main())
    print("done")
'''
{
        "user_id": "364873125218746369",
        "suppress": false,
        "session_id": "7e011d9ae36b44a4e5dd5fc2fd0d0c9d",
        "self_video": false,
        "self_mute": false,
        "self_deaf": false,
        "request_to_speak_timestamp": null,
        "mute": false,
        "deaf": false,
        "channel_id": "763224124612542508"
      }



'''