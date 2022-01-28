import requests
import sys
import os
sys.path.insert(0, os.getcwd()+"/src/master/")
import master

def authorize():
    payload = {
        "authorize":"true",
        "permissions":"0"
    }
    headers = {
        "authorization": master.read_config() 
    }