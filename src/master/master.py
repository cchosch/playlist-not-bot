from tkinter import W
import requests
import time
import json
import asyncio

epoch_tracker = {}
API_ENDPOINT = 'https://discord.com/api/v9'
def read_config():
    myconfig = open("config.json")
    re = json.load(myconfig)
    myconfig.close()
    userid = requests.get(API_ENDPOINT+"/users/@me",headers={"Authorization": re["slave_auth"]+""}).json()["id"]
    return re["master_auth"], re["master_client_id"], re["master_client_secret"], re["master_redirect_uri"], re["slave_auth"], re["prefix"], userid

MASTER_AUTH, MASTER_CLIENT_ID, MASTER_CLIENT_SECRET, MASTER_REDIRECT_URI, SLAVE_TOKEN, PREFIX, SLAVEID = read_config()

def updateVariables():
    MASTER_AUTH, MASTER_CLIENT_ID, MASTER_CLIENT_SECRET, MASTER_REDIRECT_URI, SLAVE_TOKEN, PREFIX, SLAVEID = read_config()

def exchange_code(code):
    updateVariables()
    data = {
        'client_id': MASTER_CLIENT_ID,
        'client_secret': MASTER_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': MASTER_REDIRECT_URI
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
    r.raise_for_status()
    return r.json()

def add_to_server(token, userID, guildID):
    requests.put(API_ENDPOINT+"/guilds/"+guildID+"/members/"+userID,headers={"Authorize":MASTER_AUTH},data={"access_token":token})
    
async def get_ratelimits(headers):
    return float(headers["x-ratelimit-reset"]), float(headers["x-ratelimit-remaining"])

def main():
    guilds_url = API_ENDPOINT+"/users/@me/guilds"
    epoch_tracker[guilds_url] = [time.time(), 1]
    master_auth_header = {
        "Authorization":f"Bot {MASTER_AUTH}"
    }
    while True:
        now = time.time()
        if epoch_tracker[guilds_url][0]-now > 0:
            time.sleep(epoch_tracker[guilds_url][0]-now)
        guilds_responce = requests.get(guilds_url,headers=master_auth_header)
        epoch_tracker[guilds_url][0], epoch_tracker[guilds_url][1] = get_ratelimits(guilds_responce.headers)



if __name__ == "__main__":
    main()

'''
theheader = {
    "Authorization": f"{SLAVE_TOKEN}"
}
print(requests.get(API_ENDPOINT+"/users/@me",headers=theheader).json())
'''