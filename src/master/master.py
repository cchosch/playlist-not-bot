from tkinter import W
import requests
import time
import json
import bot
import threading

guild_threads = {}
epoch_tracker = {}
API_ENDPOINT = 'https://discord.com/api/v9'
def read_config():
    myconfig = open("config.json")
    re = json.load(myconfig)
    myconfig.close()
    clientid = requests.get(API_ENDPOINT+"/users/@me", headers={"Authorization":f"Bot "+ re["master_auth"]})
    clientid = clientid.json()["id"]
    userid = requests.get(API_ENDPOINT+"/users/@me",headers={"Authorization": re["slave_auth"]+""}).json()["id"]
    return re["master_auth"], clientid, re["master_client_secret"], re["master_redirect_uri"], re["slave_auth"], re["prefix"], userid

MASTER_AUTH, MASTER_CLIENT_ID, MASTER_CLIENT_SECRET, MASTER_REDIRECT_URI, SLAVE_TOKEN, PREFIX, SLAVE_ID = read_config()

MASTER_AUTH_HEADER = {
    "Authorization":f"Bot {MASTER_AUTH}"
}

def updateVariables():
    MASTER_AUTH, MASTER_CLIENT_ID, MASTER_CLIENT_SECRET, MASTER_REDIRECT_URI, SLAVE_TOKEN, PREFIX, SLAVE_ID = read_config()

def get_ratelimits(headers):
    return float(headers["x-ratelimit-reset"]), float(headers["x-ratelimit-remaining"])

def main():
    guilds_url = API_ENDPOINT+"/users/@me/guilds"
    epoch_tracker[guilds_url] = [time.time(),1]
    guilds_responce = requests.get(guilds_url,headers=MASTER_AUTH_HEADER)
    epoch_tracker[guilds_url][0], epoch_tracker[guilds_url][1] = get_ratelimits(guilds_responce.headers)
    for guild in guilds_responce.json():
        time.sleep(0.5)
        guild_threads[guild["id"]] = threading.Thread(target = bot.read_guild_messages, args = (guild["id"],))
        print(guild["id"])
        guild_threads[guild["id"]].start()
    while True:
        if epoch_tracker[guilds_url][0]-time.time() > epoch_tracker[guilds_url][1]:
            time.sleep(epoch_tracker[guilds_url][0]-time.time())
        guilds_responce = requests.get(guilds_url,headers=MASTER_AUTH_HEADER)
        epoch_tracker[guilds_url][0], epoch_tracker[guilds_url][1] = get_ratelimits(guilds_responce.headers)
        for guild in guilds_responce.json():
            if guild == "global":
                break
            if guild["id"] not in guild_threads.keys():
                guild_threads[guild["id"]] = threading.Thread(target = bot.read_guild_messages, args = (guild["id"],))
                guild_threads[guild["id"]].start()



if __name__ == "__main__":
    main()

'''
theheader = {
    "Authorization": f"{SLAVE_TOKEN}"
}
print(requests.get(API_ENDPOINT+"/users/@me",headers=theheader).json())
'''