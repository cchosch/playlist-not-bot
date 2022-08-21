import json
import os
import random
import threading
import asyncio
import requests
import websockets
import hashlib
import time
import platform
API_ENDPOINT = 'https://discord.com/api/v9'

SLSH = "/"
if platform.system() == "Windows":
    SLSH = "\\"
PLAYLISTS_DIR = os.getcwd()+SLSH+".playlists"

if not os.path.exists(PLAYLISTS_DIR):
    os.mkdir(PLAYLISTS_DIR)
    if platform.system() == "Windows":
        import ctypes
        ctypes.windll.kernel32.SetFileAttributesW(PLAYLISTS_DIR, 0x02)

def read_config():
    myconfig = open("config.json")
    re = json.load(myconfig)
    myconfig.close()
    clientid = requests.get(API_ENDPOINT+"/users/@me", headers={"Authorization":f"Bot "+ re["master_auth"]})
    clientid = clientid.json()["id"]
    userid = "" 
    try: userid = requests.get(API_ENDPOINT+"/users/@me",headers={"Authorization": re["slave_auth"]+""}).json()["id"]
    except KeyError: pass
    return re["master_auth"], clientid, re["master_client_secret"], re["master_redirect_uri"], re["slave_auth"], re["prefix"], userid, re["apple_music_obj"]

MASTER_AUTH, MASTER_CLIENT_ID, MASTER_CLIENT_SECRET, MASTER_REDIRECT_URI, SLAVE_TOKEN, PREFIX, SLAVE_ID, APPLE_OBJ = read_config()

MASTER_AUTH_HEADER = {
    "Authorization":f"Bot {MASTER_AUTH}"
}

import commands
import notbot
import heartbeat


def read_guilds():
    return os.listdir(PLAYLISTS_DIR)

def send_message(token, channel_id, message, bot=True):
    if not bot:
        return requests.post(f"{API_ENDPOINT}/channels/{channel_id}/messages",headers={"authorization":token},data={"content":message})
    return requests.post(f"{API_ENDPOINT}/channels/{channel_id}/messages",headers={"authorization":f"Bot {token}"},data={"content":message})
    
class Playlist():
    def __init__(self, guildId: str, playlistName: str, users: dict={}, songs: list=[], public: int=0):
        self._guildId = guildId
        self._name = playlistName
        self.update_path()
        self.update_dir()
        self.already_exists = False
        try:
            self.update_from_file()
            self.already_exists = True
        except FileNotFoundError:
            self.users = users
            self.songs = songs
            self.public = public

    @property
    def guildId(self):
        return self._guildId

    @guildId.setter
    def guildId(self, new_val):
        self._guildId = new_val
        self.update_path()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_val):
        self._name = new_val
        self.update_path()

    def update_from_file(self) -> dict:
        if not os.path.exists(self.update_dir()):
            raise FileNotFoundError(self.dir)
        
        file = open(self.path, "r")
        contents = json.loads(file.read().strip())
        file.close()
        try:
            self.users = contents["users"]
            self.public = contents["public"]
            self.songs = contents["songs"]
        except KeyError as e:
            print(f"KEY ERROR update_from_file: \nJSON FILE PATH: {self.path} \n{e}")
            return {}
        return contents

    def update_path(self) -> str:
        #           dir to pfold         guildid             md5 hashed name
        self.path =  PLAYLISTS_DIR +SLSH+ self.guildId +SLSH+ hashlib.md5(self.name.encode()).hexdigest()
        self.update_dir()
        return self.path
    
    def update_dir(self) -> str:
        self.dir = PLAYLISTS_DIR +SLSH+ self.guildId +SLSH
        return self.dir

    def remove_user(self, uid) -> None:
        self.users.pop(uid, None)
    
    def add_user(self, uid, auth_level) -> None:
        self.users[uid] = auth_level

    def get_user_auth(self, uid) -> int:
        return self.users.get(uid, self.public)
    
    def set_default_auth(self, auth):
        self.public = auth

    def save(self) -> None:
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
            
        file = open(self.path, "w")
        file.write(json.dumps({
            "users": self.users,
            "public": self.public,
            "songs": self.songs
        }, indent=2))
        file.close()


class Bot():
    def __init__(self):
        self.voice_states = {} # voice states
        self.notBot = notbot.NotBot(self)
        self.SEQUENCE_NUM = None
        self.SESSION_ID = None

    async def main(self):
        threading.Thread(target=self.notBot.start_loop).start()
        new_ws = API_ENDPOINT+"/gateway"
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
                    except websockets.ConnectionClosedError:
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
                            if res["d"]["content"] != "" and res["d"]["content"][0] == PREFIX:
                                command :str = (res["d"]["content"].split(" ")[0]).removeprefix(PREFIX)
                                if command in commands.Commands.keys():
                                    await commands.Commands[command](res, self)
                                else:
                                    requests.post(f"{API_ENDPOINT}/channels/"+res["d"]["channel_id"]+"/messages",headers=MASTER_AUTH_HEADER,data={"content":"Unkown command: "+command})
if __name__ == "__main__":
    mybot = Bot()
    asyncio.run(mybot.main())