import requests
import time
import sys
import os
sys.path.insert(0, os.getcwd()+"/src/slave")
from slave import *
from master import *
bot_epoch_tracker = {}

def read_guild_messages(guildid):
    bot_epoch_tracker[guildid] = [time.time(), 1]
    members = requests.get(f"{API_ENDPOINT}/guilds/{guildid}/members/{SLAVE_TOKEN}",headers=MASTER_AUTH_HEADER)
    if members.json()["code"] == 50035:
        add_to_guild(refresh_token(exchange_code(get_code())["refresh_token"])["access_token"],guildid)
    quit()
    while True:
        time.sleep(0.3)
        guild_responce = requests.get(API_ENDPOINT+"/guilds/"+guildid,headers=MASTER_AUTH_HEADER)
        print(guild_responce.content)
    quit()

