from flask import Flask, request
import json
import os
from datetime import datetime

app = Flask(__name__)

users = {"admin": "1234"}

# 🔥 FIX: path assoluto stabile
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
LOG_FILE = os.path.join(DATA_DIR, "logs.json")

# crea cartella se non esiste
os.makedirs(DATA_DIR, exist_ok=True)


def log_event(event):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(event) + "\n")
    except Exception as e:
        print("LOG ERROR:", e)


@app.route("/login", methods=["POST"])
def login():
    try:
        username = request.form.get("username")
        password = request.form.get("password")
        ip = request.remote_addr

        success = users.get(username) == password

        log_event({
            "timestamp": str(datetime.now()),
            "ip": ip,
            "event": "login_attempt",
            "success": success
        })

        return "OK" if success else "FAIL"

    except Exception as e:
        print("ROUTE ERROR:", e)
        return "SERVER ERROR", 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)