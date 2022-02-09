import requests
import time
import sys
import threading
from inspect import currentframe, getframeinfo
import os
import json
sys.path.insert(0, os.getcwd()+"/src/slave")
from slave import *
from master import *
bot_epoch_tracker = {}


def add_slave_to_guild(guildid):
    members = requests.get(f"{API_ENDPOINT}/guilds/{guildid}/members/{SLAVE_ID}",headers=MASTER_AUTH_HEADER)
    try:
        if members.json()["code"] == 10007:
            add_to_guild(refresh_token(exchange_code(get_code())["refresh_token"])["access_token"],guildid)
    except KeyError:
        pass

def add_song(guildid, userid, args):
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
    
    
         
    
