import requests
import json
import time
import threading
import asyncio
import websockets
from master import *
from heartbeat import *


async def repeat():
    while True:
        asyncio.sleep(.2)
        print("x")


def main():
    asyncio.run(repeat())

themain = threading.Thread(target=main)
themain.start()
