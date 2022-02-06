import requests
import time
import sys
import threading
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
        for channel in channels.json():
            if f"{API_ENDPOINT}/channels/"+channel["id"]+"/messages" not in epoch_tracker.keys():
                epoch_tracker[f"{API_ENDPOINT}/channels/"+channel["id"]+"/messages"] = [time.time(), 1]
            if channel["type"] != 0:
                continue
            if channel["id"] not in read_messages.keys():
                read_messages[channel["id"]] = ["" for i in range(10)]
                print("RESET")
            if epoch_tracker[f"{API_ENDPOINT}/channels/"+channel["id"]+"/messages"][0]-time.time() > 0:
                time.sleep(epoch_tracker[f"{API_ENDPOINT}/channels/"+channel["id"]+"/messages"][0]-time.time())
            messages = requests.get(f"{API_ENDPOINT}/channels/"+channel["id"]+"/messages",headers=MASTER_AUTH_HEADER)
            epoch_tracker[f"{API_ENDPOINT}/channels/"+channel["id"]+"/messages"][0], epoch_tracker[f"{API_ENDPOINT}/channels/"+channel["id"]+"/messages"][1] = get_ratelimits(messages.headers)
            messages = messages.json()
            for i in range(len(messages)):
                if i > 9:
                    break
                if  str(messages[i]["id"]) not in read_messages[channel["id"]] and conv_utime(messages[i]["timestamp"])-start > 0:
                    read_messages[channel["id"]].pop(len(read_messages[channel["id"]])-1)
                    read_messages[channel["id"]].insert(0, messages[i]["id"])
                    try:
                        messages[i]["content"][0]
                    except IndexError:
                        continue
                    if messages[i]["content"][0] == PREFIX:
                        theargs = messages[i]["content"].split()
                        if theargs[0] == f"{PREFIX}add":
                            add_song(guildid,theargs)
                        if theargs[0] == f"{PREFIX}play":
                            try:
                                threading.Thread(target=play_playlist,args=(theargs[1], guildid, channel["id"], theargs[2])).start()
                            except:
                                pass

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
    
    
         
    
