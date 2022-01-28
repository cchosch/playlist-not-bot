import requests
import json
API_ENDPOINT = 'https://discord.com/api/v8'

def read_config():
    myconfig = open("config.json")
    re = json.load(myconfig)
    myconfig.close()
    return re["master_auth"], re["master_client_id"], re["master_client_secret"], re["master_redirect_uri"], re["slave_auth"], re["prefix"] 

MASTER_AUTH, MASTER_CLIENT_ID, MASTER_CLIENT_SECRET, MASTER_REDIRECT_URI, SLAVE_TOKEN, PREFIX = read_config()

def exchange_code(code):
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


theheader = {
    "Authorization": f"Bot {MASTER_AUTH}"
}
print(requests.get(API_ENDPOINT+"/users/@me/guilds",headers=theheader).json()[0])