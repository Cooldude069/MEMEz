from threading import Thread
from flask import Flask

"""
This file is used to keep the bot running on Replit 24/7.
Creating a simple Flask app and pinging it every 5 mins will keep it online forever.
"""

app = Flask("")


@app.route("/")
def home():
    return "Bot running"


def run():
    app.run(host="0.0.0.0", port=8080)


def start():
    t = Thread(target=run)
    t.start()
