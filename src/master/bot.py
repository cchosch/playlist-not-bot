import requests
import time
from master import *
bot_epoch_tracker = {}

def read_guild_messages(guildid):
    bot_epoch_tracker[guildid] = [time.time(), 1]
    while True:
        for guild in guild_tracker:
            print(guild)
            time.sleep(2)

    