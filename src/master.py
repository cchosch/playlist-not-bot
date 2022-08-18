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
    return re["master_auth"], clientid, re["master_client_secret"], re["master_redirect_uri"], re["slave_auth"], re["prefix"], userid

MASTER_AUTH, MASTER_CLIENT_ID, MASTER_CLIENT_SECRET, MASTER_REDIRECT_URI, SLAVE_TOKEN, PREFIX, SLAVE_ID = read_config()

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
    
class Playlist_File():
    @staticmethod
    def get_playlist_dir(guildid, playlist: str) -> str:
        #      dir to pfold         guildid        md5 hashed playlist name
        return PLAYLISTS_DIR +SLSH+ guildid +SLSH+ hashlib.md5(playlist.encode()).hexdigest()
        pass

    @staticmethod
    def update_playlist(guildid, playlist : str, json_obj: dict):
        pdir = Playlist_File.get_playlist_dir(guildid, playlist)
        if not os.path.exists(pdir):
            print(f"UPDATE_PLAYLIST path doesn't exists \nguildid: {guildid}\nplaylistname: {playlist}\nfile_dir: {pdir}")
            return

        file = open(pdir, "w")
        file.write(json.dumps(json_obj, indent=2))
        file.close()

    def get_playlist(guildid, playlist) -> dict:
        file = open(Playlist_File.get_playlist_dir(guildid, playlist), "r")
        contents = json.loads(file.read())
        file.close()
        return contents

    @staticmethod
    def create_playlist(guildid, playlist : str, json_obj: dict):
        pdir = Playlist_File.get_playlist_dir(guildid, playlist)
        if os.path.exists(pdir):
            print(f"CREATE_PLAYLIST path exists \nguildid: {guildid}\nplaylistname: {playlist}\nfile_dir: {pdir}")
            return 
        if not os.path.exists(PLAYLISTS_DIR+SLSH+guildid):
            os.mkdir(PLAYLISTS_DIR+SLSH+guildid)
            
        file = open(pdir, "w")
        file.write(json.dumps(json_obj, indent=2))
        file.close()

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