import requests
import json
import time
import threading
from master import *


def add_song_to_file(guildid, playlist, song):

    playlists_file = open("playlists.json")
    playlists_obj = json.load(playlists_file)
    playlists_file.close()
    found = False
    for guild in playlists_obj:
        if guild["id"] == guildid:
            found = True
            if playlist in guild["playlists"].keys():
                guild["playlists"][playlist].append(song)
            continue
    if not found:
        playlists_obj.append({
            "id":guildid,
            "playlists":{
                playlist:[song]
            }
        })

    playlists_file = open("playlists.json","w")
    playlists_file.write(json.dumps(playlists_obj,indent=2))
    playlists_file.close()
