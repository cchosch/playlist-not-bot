import requests
import sys
import random
import os
import time
import json
sys.path.insert(0, os.getcwd()+"/src/master/")
from master import *
from urllib.parse import urlparse
from urllib.parse import parse_qs

def get_code():
    payload = json.dumps({
    "permissions":0,
    "authorize":True
    })
    header = {
        "Authorization":f"{SLAVE_TOKEN}",
        "content-type":"application/json"
    }

    nextrequest = requests.post(API_ENDPOINT+"/oauth2/authorize?client_id=932752503769018428&response_type=code&redirect_uri=http://71.191.132.246%2F&scope=identify%20guilds.join&state=15773059ghq9183habn",headers=header,data=payload).json()["location"]
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

def play_playlist( playlist, channelid, prefix):
    for song in playlist:
        time.sleep(2+random.uniform(0.0,0.3))
        requests.post(API_ENDPOINT+"/channels/"+channelid+"/messages",headers={"Authorization":f"{SLAVE_TOKEN}"},data={"content":f"{prefix}play "+song})

