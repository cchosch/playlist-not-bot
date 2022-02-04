import requests
import time
import sys
import os
import json
import dateutil.parser as dp
sys.path.insert(0, os.getcwd()+"/src/slave")
from slave import *
from master import *
bot_epoch_tracker = {}

def conv_utime(timestamp):
    return dp.parse(timestamp).timestamp()

def read_guild_messages(guildid):
    read_messages = {}
    members = requests.get(f"{API_ENDPOINT}/guilds/{guildid}/members/{SLAVE_ID}",headers=MASTER_AUTH_HEADER)
    try:
        if members.json()["code"] == 10007:
            add_to_guild(refresh_token(exchange_code(get_code())["refresh_token"])["access_token"],guildid)
    except KeyError:
        pass
    start = time.time()
    last = time.time()-5
    channels_url = f"{API_ENDPOINT}/guilds/{guildid}/channels"
    epoch_tracker[channels_url] = [time.time(),1]
    channels = requests.get("https://google.com")
    while True:
        if epoch_tracker[channels_url][0]-time.time() < 0:
            channels = requests.get(channels_url,headers=MASTER_AUTH_HEADER)
            epoch_tracker[channels_url][0], epoch_tracker[channels_url][1] =get_ratelimits(channels.headers)
        print(channels.content)
        for channel in channels.json():
            if channel["type"] != 0:
                continue
            if channel["id"] not in read_messages.keys():
                read_messages[channel["id"]] = ["" for i in range(10)]
            messages = requests.get(f"{API_ENDPOINT}/channels/"+channel["id"]+"/messages",headers=MASTER_AUTH_HEADER)
            print(messages)
            messages = messages.json
            for i in range(len(messages)):
                if i > 9:
                    break
                if messages[i]["id"] not in read_messages and conv_utime(messages[i]["timestamp"])-start > 0:
                    read_messages[channel["id"]].pop(len(read_messages)-1)
                    read_messages[channel["id"]].append(messages[i]["id"])
                    try:
                        messages[i]["content"][0]
                    except IndexError:
                        continue
                    if messages[i]["content"][0] == PREFIX:
                        theargs = messages[i]["content"].split()
                        if theargs[0] == f"{PREFIX}add":
                            add_song(guildid,theargs)

def add_song(guildid, args):
    '''
    playlist.json format:
    [
        {
            "id": "GUILDID1",
            "playlists": {
                "firstplaylist":["example song", "example song"],
                "secondplaylist":["example song", "example song"]
            }
        }
        {
            "id": "GUILDID2",
            "playlists":{
                "firstplaylist":["example song", "example song"],
                "secondplaylist":["example song","example song"]
            }
        }
    ]
    '''
    
    print("HELLO")
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
            playlists: {
                playlist:[song]
            }
        })
    json.dumps(playlist_servers)
    playlist_file = open("playlists.json", "w")
    
     
            
         
    
