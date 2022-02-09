import asyncio
import json
import random
import threading
import time
import websockets
from argparse import ArgumentError
from websockets.legacy.client import WebSocketClientProtocol

class Heartbeat(threading.Thread):
    def __init__(self, **kwargs):
        super(Heartbeat,self).__init__(**kwargs)
        self.websocket : WebSocketClientProtocol = None
        self.interval = 0
        self.snum = None
        for a in kwargs.keys():
            if a == "args":
                self.websocket = kwargs[a][0]
                self.interval = kwargs[a][1]
                continue
        if self.websocket == None or self.interval == None:
            ArgumentError(message="NO ARGUMENTS PASSED TO HEARTBEAT CONSTRUCTOR")
        self.stop = False
    
    def stop_exe(self):
        self.stop = True
        
    def run(self):
        time.sleep(self.interval*random.uniform(0.1,0.9))
        while self.snum == None:
            time.sleep(0.1)
        asyncio.run(self.websocket.send(json.dumps({"op":1,"d":self.snum})))
        quit()
        last = time.time()
        while not self.stop:
            time.sleep(0.2)
            if time.time()-last >= self.interval:
                asyncio.run(self.websocket.send(json.dumps({"op":1,"d":self.snum})))
                last = time.time()
        