import requests
import asyncio
import json
from master import *

def get_attributes_from_res(res):

    return {
        "authorid": res["d"]["author"]["id"],
        "guildid": res["d"]["guild_id"],
        "channelid": res["d"]["channel_id"],
    }

async def create(res, bot):
    pass

async def add(res, bot):
    args = res["d"]["content"].split(" ")
    attribs = get_attributes_from_res(res)
    if len(args) < 3:
        send_message(MASTER_AUTH, attribs["channelid"],"This does not make sense.")
        return
    playlist = args[1]
    song = " ".join(args[2:len(args)])

    cplaylist = Playlist(attribs["guildid"], playlist, users={attribs["authorid"]:4}, songs=[song], public=0)
    if cplaylist.get_user_auth(attribs["authorid"]) < 2:
        send_message(MASTER_AUTH, attribs["channelid"], "You're not authorized to add songs to this playlist. Sucks to suck!")
        return

    if cplaylist.already_exists:
        cplaylist.songs.append(song)
        cplaylist.save()
        send_message(MASTER_AUTH, attribs["channelid"], f"Added {song} to {playlist}.")
        return

    cplaylist.save()
    send_message(MASTER_AUTH, attribs["channelid"], f"Created playlist called {playlist} and added {song} to it.")

async def clear_playlist(res, bot):
    args = res["d"]["content"].split(" ")
    attribs = get_attributes_from_res(res)
    if len(args) > 2 or len(args) < 2:
        send_message(MASTER_AUTH, attribs["channelid"], "Please use 1 argument (the name of the playlist).")
        return

    playlist = args[1]
    cplaylist = Playlist(attribs["guildid"], playlist)
    if not cplaylist.already_exists:
        send_message(MASTER_AUTH, attribs["channelid"], f"{playlist} doesn't exist")
        return

    cplaylist.songs = []
    cplaylist.save()
    send_message(MASTER_AUTH, attribs["channelid"], f"Cleared all songs in {playlist}")

async def play(res, bot):
    args = res["d"]["content"].split(" ")
    attribs = get_attributes_from_res(res)
    if len(args) < 3 or len(args) > 3:
        send_message(MASTER_AUTH, attribs["channelid"], "I dont understand what you just said.")
        return

    playlist = args[1]
    cplaylist = Playlist(attribs["guildid"], playlist)
    if not cplaylist.already_exists:
        send_message(MASTER_AUTH, res["d"]["channel_id"], f"{playlist} doesn't exist.")
        return
    
    await bot.notBot.ws.send(json.dumps({
        "op":4,
        "d":{
            "guild_id": attribs["guildid"],
            "channel_id":bot.voice_states[attribs["authorid"]]["channel_id"],
        }
    }))

    for song in cplaylist.songs:
        send_message(SLAVE_TOKEN, res["d"]["channel_id"], f"{args[2]}play "+song, bot=False)
        time.sleep(2)

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
    "clear-playlist":clear_playlist,
    "play":play,
    "settings":settings,
    "plist-settings":psettings
}
