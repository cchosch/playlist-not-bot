import requests
import json
from master import *
from master.master import MASTER_AUTH

print(API_ENDPOINT)

class Bot():
    def __init__(self):
        self.ratelimits = {}

    def updateGuilds(self):
        requests.get(API_ENDPOINT+"/users/@me/guilds",headers={"Authorizaiton":f"Bot {MASTER_AUTH}"})

    def get_new_messages(self):
        pass

    