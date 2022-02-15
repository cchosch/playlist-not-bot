import requests
import sys
import asyncio
import threading
from inspect import currentframe, getframeinfo
import os
import json
from heartbeat import *
import websockets
from slave import *
from master import *
bot_epoch_tracker = {}

class Bot():
    def __init__(self):
        self.reset()

    def reset(self):
        self.ws = None
        self.heartbeat = None
        self.running = True
        self.snum = None
    def start_loop(self):
        asyncio.run(self.main_loop())

    def quit_exe(self):
        self.running = False
        self.ws.send("jghrueohtiroeh")

    async def main_loop(self):
        print("starting bot loop...")
        new_ws = API_ENDPOINT+"/gateway?v=4"
        while self.running:
            cws = requests.get(new_ws,headers=MASTER_AUTH_HEADER).json()["url"]
            self.ws = await websockets.connect(cws)
            print("connected to websocket on bot")
            interval = (json.loads(await self.ws.recv())["d"]["heartbeat_interval"])/1000
            self.heartbeat = Heartbeat(args=(self.ws, interval))
            self.heartbeat.start()
            await self.ws.send(json.dumps({
                "op":2,
                "d":{
                    "token":f"{SLAVE_TOKEN}",
                    "properties":{
                        "$os":"win",
                        "$browser:":"disco",
                        "$device":"disco"
                    }
                }
            }))
            while self.running:
                x = json.loads(await self.ws.recv())
                if x["s"] != None:
                  self.snum = x["s"]
                  self.heartbeat.snum = x["s"]
                print("SLAVE\n"+json.dumps(x,indent=2))

def add_song(self, guildid, uid, args):
    playlist = args[1]
    song = " ".join(args[2:len(args)])
    playlist_file = open("playlists.json")
    playlist_servers = json.load(playlist_file)
    playlist_file.close()
    found = False
    for ps in playlist_servers:
        if ps["id"] == guildid:
            found = True
            if playlist in ps["playlists"].keys():
                ps["playlists"][playlist].append(song)
            else:
                ps["playlists"][playlist] = [song]
    if not found:
        playlist_servers.append({
            "id":guildid,
            "playlists": {
                playlist:[song]
            }
        })
    playlist_file = open("playlists.json", "w")
    playlist_file.write(json.dumps(playlist_servers,indent=2))
    playlist_file.close()

         

def add_slave_to_guild( guildid):
    members = requests.get(f"{API_ENDPOINT}/guilds/{guildid}/members/{SLAVE_ID}",headers=MASTER_AUTH_HEADER)
    try:
        if members.json()["code"] == 10007:
            add_to_guild(refresh_token(exchange_code(get_code())["refresh_token"])["access_token"],guildid)
    except KeyError:
        pass
