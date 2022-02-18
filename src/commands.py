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
    args = res["d"]["content"].split(" ")
    if len(args) < 3:
        send_message(MASTER_AUTH, res["d"]["channel_id"], "i dont understand what you just said")
        return
    guilds = read_guilds()
    await bot.notBot.ws.send(json.dumps({
        "op":4,
        "d":{
            "guild_id":res["d"]["guild_id"],
            "channel_id":bot.voice_states[res["d"]["author"]["id"]]["channel_id"],
        }
    }))
    found = False
    for guild in guilds:
        if guild["id"] == res["d"]["guild_id"]:
            found = True
            if args[1] in guild["playlists"].keys():
                for song in guild["playlists"][args[1]]["songs"]:
                    send_message(SLAVE_TOKEN, res["d"]["channel_id"], f"{args[2]}play "+song,bot=False)
                    time.sleep(2)
            else:
                found = False
            break
    if found == False:
        send_message(MASTER_AUTH, res["d"]["channel_id"], "could not find your playlist")
        return
    await bot.notBot.ws.send(json.dumps({
        "op":4,
        "d":{
            "guild_id":res["d"]["guild_id"],
            "channel_id": None,
        }
    }))

async def settings(res, bot):
    uid = res["d"]["author"]["id"]
    args = res["d"]["content"].split(" ")
    if len(args) < 3:
        send_message(MASTER_AUTH, res["d"]["channel_id"], "i dont understnad")
        quit()
    if args[1] == "prefix":
        pass
    else:
        gid = res["d"]["guild_id"]
        guilds = read_guilds()
        for guild in guilds:
            if guild["id"] == gid:
                if args[1] in guild["playlists"].keys():
                    plist = guild["playlists"][args[1]]
                    if args[2] == "public":
                        if len(args) < 4 or  type(args[3]) != int or 0 > args[3] > 4:
                            send_message(MASTER_AUTH, res["d"]["channel_id"], "i dont understand")
                            break
                        else:
                            plist["public"] = args[3]
                            send_message(MASTER_AUTH, res["d"]["channel_id"], "set "+args[1]+" public to "+args[3])
                            return
                            
                break
        send_message(MASTER_AUTH, res["d"]["channel_id"], "i dont know what you mean")
    

async def psettings(res, bot):
    pass


Commands = {
    "add":add,
    "play":play,
    "settings":settings,
    "plist-settings":psettings
}
