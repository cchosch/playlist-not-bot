import requests
import sys
import random
import os
import asyncio
import json

sys.path.insert(0, os.getcwd()+"/src/master/")
from master import *

async def get_code(self):
    payload = json.dumps({
    "permissions":0,
    "authorize":True
    })
    header = {
        "Authorization":f"{SLAVE_TOKEN}",
        "content-type":"application/json"
    }

    nextrequest = requests.post(API_ENDPOINT+"/oauth2/authorize?client_id=932752503769018428&response_type=code&redirect_uri=http%3A%2F%2Fcolinhapi.com%2F&scope=identify%20guilds.join&state=15773059ghq9183habn",headers=header,data=payload).json()["location"]
    asyncio.sleep(0.1)
    requests.get(nextrequest)

async def play_playlist(self, playlist, channelid, prefix):
    for song in playlist:
        asyncio.sleep(2+random.uniform(0.0,0.3))
        requests.post(API_ENDPOINT+"/channels/"+channelid+"/messages",headers={"Authorization":f"{SLAVE_TOKEN}"},data={"content":f"{prefix}play "+song})

