from flask import Flask 
from flask import request
from master import exchange_code
import sys
import os

app = Flask(__name__)

@app.route("/")
def get():
    print(request.args.get("code"))
    print(exchange_code(request.args.get("code")))
    return ""

app.run(port=5000)
