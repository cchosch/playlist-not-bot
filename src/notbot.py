import requests
import sys
import asyncio
import threading
import os
import json
import websockets
from urllib.parse import urlparse
from urllib.parse import parse_qs
from heartbeat import *
from master import *

class NotBot():
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

def get_code():
    payload = json.dumps({
    "permissions":0,
    "authorize":True
    })
    header = {
        "Authorization":f"{SLAVE_TOKEN}",
        "content-type":"application/json"
    }

    nextrequest = requests.post(f"{API_ENDPOINT}/oauth2/authorize?client_id={MASTER_CLIENT_ID}&response_type=code&redirect_uri={MASTER_REDIRECT_URI}&scope=identify%20guilds.join&state=15773059ghq9183habn",headers=header,data=payload).json()["location"]
    return parse_qs(urlparse(nextrequest).query)["code"][0]

def exchange_code(code): # ripped from https://discord.com/developers/docs/topics/oauth2
    data = {
        "client_id": MASTER_CLIENT_ID,
        "client_secret": MASTER_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": MASTER_REDIRECT_URI
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post(f"{API_ENDPOINT}/oauth2/token", data=data, headers=headers)
    r.raise_for_status()
    return r.json()

def refresh_token(refresh_token): # ripped from https://discord.com/developers/docs/topics/oauth2
    data = {
        "client_id": MASTER_CLIENT_ID,
        "client_secret": MASTER_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    r = requests.post(f"{API_ENDPOINT}/oauth2/token", data=data, headers=headers)
    return r.json()
  
def add_to_guild(access_token, guildID): # ripped from https://dev.to/dandev95/add-a-user-to-a-guild-with-discord-oauth2-in-python-using-requests-595f
    data = {
        "access_token" : access_token,
    }
    headers = {
        "Authorization" : f"Bot {MASTER_AUTH}",
        "Content-Type": "application/json"
    }
    print(requests.put(f"{API_ENDPOINT}/guilds/{guildID}/members/{SLAVE_ID}", headers=headers, json=data))

def play_playlist(playlist_name, guildid, channelid, prefix):
    playlist_file = open("playlists.json")
    p_obj = json.load(playlist_file)
    playlist_file.close()
    for g in p_obj:
        if g["id"] == guildid:
            for playlists in g["playlists"].keys():
                if playlists == playlist_name:
                    for song in g["playlists"][playlist_name]:
                        time.sleep(2.5+random.uniform(0.0,0.3))
                        requests.post(API_ENDPOINT+"/channels/"+channelid+"/messages",headers={"Authorization":f"{SLAVE_TOKEN}"},data={"content":f"{prefix}play "+song})

         

def add_slave_to_guild( guildid):
    members = requests.get(f"{API_ENDPOINT}/guilds/{guildid}/members/{SLAVE_ID}",headers=MASTER_AUTH_HEADER)
    try:
        if members.json()["code"] == 10007:
            add_to_guild(refresh_token(exchange_code(get_code())["refresh_token"])["access_token"],guildid)
    except KeyError:
        pass
