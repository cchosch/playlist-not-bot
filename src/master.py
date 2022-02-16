import json
import random
import threading
import asyncio
import requests
import websockets
import time
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

import commands
import notbot
import heartbeat

def send_message(token, channel_id, message, bot=False):
    if not bot:
        print(type(channel_id))
        return requests.post(f"{API_ENDPOINT}/channels/{channel_id}/messages",headers={"authorization":token},data={"content":message})
    return requests.post(f"{API_ENDPOINT}/channels/{channel_id}/messages",headers={"authorization":f"Bot {token}"},data={"content":message})


class Bot():
    def __init__(self):
        self.voice_states = {} # voice states
        self.notBot = notbot.NotBot(self)
        self.SEQUENCE_NUM = None
        self.SESSION_ID = None

    async def main(self):
        threading.Thread(target=self.notBot.start_loop).start()
        new_ws = API_ENDPOINT+"/gateway?v=4"
        while True:
            print("connecting to websocket...")
            cws = requests.get(new_ws,headers=MASTER_AUTH_HEADER).json()["url"]
            async with websockets.connect(cws) as ws:
                if self.SESSION_ID != None:
                    await ws.send(json.dumps({
                        "op": 6,
                        "d": {
                            "token": f"Bot {MASTER_AUTH}",
                            "session_id": self.SESSION_ID,
                            "seq": self.SEQUENCE_NUM
                        }
                    }))
                    print("DEBUG DATA")
                    print(f"TOKEN: {MASTER_AUTH}, {type(MASTER_AUTH)}")
                    print(f"SESSION_ID: {self.SESSION_ID}, {type(self.SESSION_ID)}")
                    print(f"SEQUENCE NUMBER: {self.SEQUENCE_NUM}, {type(self.SEQUENCE_NUM)}")
                else:
                    await ws.send(json.dumps({
                        "op":2,
                        "d":{"token":f"Bot {MASTER_AUTH}","properties":{"$os":"win","$browser:":"disco","$device":"disco"}}
                    }))
                interval = (json.loads(await ws.recv())["d"]["heartbeat_interval"])/1000
                MAIN_HEARTBEAT = heartbeat.Heartbeat(args=(ws, interval))
                MAIN_HEARTBEAT.start()
                print("connected")
                while True:
                    try:
                        res = json.loads(await ws.recv())
                    except json.ConnectionClosedError:
                        continue
                    #print("MASTER\n"+json.dumps(res,indent=2))
                    if res["s"] != None:
                        self.SEQUENCE_NUM = res["s"]
                        MAIN_HEARTBEAT.snum = res["s"] 
                    if res["op"] == 9:
                        print("RECEIVED OP CODE 9")
                        MAIN_HEARTBEAT.stop_exe()
                        break
                    if res["op"] == 0:
                        if res["t"] == "READY":
                            self.SESSION_ID = res["d"]["session_id"]
                            continue
                        if res["t"] == "VOICE_STATE_UPDATE":
                            self.voice_states[res["d"]["user_id"]] = res["d"]
                        if res["t"] == "GUILD_CREATE":
                            time.sleep(.3)
                            notbot.add_slave_to_guild(res["d"]["id"])
                            if res["d"]["voice_states"] != []:
                                for s in res["d"]["voice_states"]:
                                    s["guild_id"] = res["d"]["id"]
                                    s["member"] = requests.get(API_ENDPOINT+"/guilds/"+res["d"]["id"]+"/members/"+s["user_id"],headers=MASTER_AUTH_HEADER).json()
                                    self.voice_states[s["user_id"]] = s
                        if res["t"] == "MESSAGE_CREATE":
                            if res["d"]["content"] != "":
                                if res["d"]["content"][0] == PREFIX:
                                    command = res["d"]["content"].split(" ")[0]
                                    command = command[1:len(command)]
                                    if command in commands.Commands.keys():
                                        await commands.Commands[command](res, self)
                                    else:
                                        requests.post(f"{API_ENDPOINT}/channels/"+res["d"]["channel_id"]+"/messages",headers=MASTER_AUTH_HEADER,data={"content":"Unkown command: "+command})
if __name__ == "__main__":
    mybot = Bot()
    asyncio.run(mybot.main())