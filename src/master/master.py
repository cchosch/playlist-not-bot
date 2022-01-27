from re import I
import discord
from discord.ext import commands
import json
import slave


def read_config():
    config = open("config.json")
    re =json.load(config)
    config.close()
    return re

class Bot(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
        self.prefix = read_config()["prefix"]
    async def on_ready(self):
        print(self.user)
    async def on_message(self,msg):
        if msg.content[0] == self.prefix:
            print("COMMAND RECEIVED")
        print(msg.content)


client = Bot()
client.run(read_config()["master_auth"])

