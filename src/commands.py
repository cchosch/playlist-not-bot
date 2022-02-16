import requests
import asyncio
import json
from master import *


async def add(res, bot):
    args = res["d"]["content"].split(" ")
    if len(args) < 3:
        send_message(SLAVE_TOKEN, res["d"]["channel_id"],"this does not make sense")
        return
    ownerid = res["d"]["author"]["id"]
    guildid = res["d"]["guild_id"]
    playlist = args[1]
    song = " ".join(args[2:len(args)])

    playlist_file = open("playlists.json")
    try:
        playlist_servers = json.load(playlist_file)
    except json.JSONDecodeError:
        playlist_servers= []
    playlist_file.close()

    found = [False for i in range(2)]
    for ps in playlist_servers:
        try:
            ps["id"]
        except KeyError:
            playlist_servers = []
            break
        if ps["id"] == guildid:
            found[0] = True
            for play in ps["playlists"].keys():
                if playlist == play:
                    found[1] = True
                    if ownerid in ps["playlists"][play]["users"].keys():
                        if ps["playlists"][play]["users"][ownerid] != None:
                            ps["playlists"][play]["songs"].append(song)
                            send_message(MASTER_AUTH,res["d"]["channel_id"], f"added {song} to {playlist}",bot=True)
                    else:
                        send_message(MASTER_AUTH, res["d"]["channel_id"], "You are not authorized to add songs to this playlist. Sucks to suck!", bot=True)
            if found[1] == False:
                ps["playlists"][playlist] = {
                    "users":{
                        ownerid: 5
                    },
                    "public":0,
                    "songs":[song]
                }
                send_message(MASTER_AUTH, res["d"]["channel_id"], "Created new playlist called "+playlist, bot=True)
            break
    if not found[0]:
        playlist_servers.append({
            "id":guildid,
            "playlists": {
                playlist:{
                    "users":{
                        ownerid: 5
                    },
                    "public": 0,
                    "songs":[song]
                }
            }
        })
        send_message(MASTER_AUTH, res["d"]["channel_id"], "Created new playlist called "+playlist, bot=True)

    playlist_file = open("playlists.json", "w")
    playlist_file.write(json.dumps(playlist_servers,indent=2))
    playlist_file.close()

async def play(res, bot):
    await bot.notBot.ws.send(json.dumps({
        "op":4,
        "d":{
            "guild_id":res["d"]["guild_id"],
            "channel_id":bot.voice_states[res["d"]["author"]["id"]]["channel_id"],
        }
    }))
    time.sleep(2)
    await bot.notBot.ws.send(json.dumps({
        "op":4,
        "d":{
            "guild_id":res["d"]["guild_id"],
            "channel_id": None,
        }
    }))

Commands = {
    "add":add,
    "play":play
}
