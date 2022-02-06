import requests
import json
import time
import threading
from master import *
inputs = ["" for i in range(10)]
while True:
    ti = input()
    if ti not in inputs:
        inputs.pop(len(inputs)-1)
        inputs.insert(0,ti)
        print(inputs)
