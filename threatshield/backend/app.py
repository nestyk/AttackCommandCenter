from flask import Flask, render_template
from flask_socketio import SocketIO
import json
import time
import threading
import requests
from collections import defaultdict
import os

app = Flask(__name__, template_folder="../dashboard/templates")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "../data/logs.json")


# ---------------- DETECTION ----------------
def detect_attacks():
    attempts = defaultdict(int)
    alerts = []

    try:
        with open(LOG_FILE) as f:
            for line in f:
                log = json.loads(line)
                if log.get("event") == "login_attempt" and not log.get("success"):
                    attempts[log.get("ip")] += 1
    except:
        pass

    for ip, count in attempts.items():
        if count >= 3:
            alerts.append({
                "type": "Brute Force",
                "ip": ip,
                "count": count,
                "severity": "HIGH"
            })

    return alerts


# ---------------- CVE FEED ----------------
def fetch_cves():
    try:
        r = requests.get("https://cve.circl.lu/api/last", timeout=5)
        return r.json()[:5]
    except:
        return []


# ---------------- REALTIME LOOP ----------------
def background_loop():
    while True:
        logs = []

        try:
            with open(LOG_FILE) as f:
                logs = [json.loads(l) for l in f if l.strip()]
        except:
            pass

        data = {
            "logs": logs[::-1][:20],
            "alerts": detect_attacks(),
            "cves": fetch_cves()
        }

        socketio.emit("update", data)

        print("📡 emitted update")  # DEBUG importante

        time.sleep(3)


# ---------------- ROUTE ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- START ----------------
if __name__ == "__main__":
    thread = threading.Thread(target=background_loop)
    thread.daemon = True
    thread.start()

    socketio.run(app, host="127.0.0.1", port=8000, debug=True)