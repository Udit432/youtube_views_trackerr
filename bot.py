import requests
import time
import threading
from datetime import datetime
from flask import Flask

# ===== CONFIG =====
API_KEY = "YOUR_YOUTUBE_API_KEY"
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# ===== FLASK (anti-sleep server) =====
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# ===== TELEGRAM =====
def send_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": text})

def get_views(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={API_KEY}"
    res = requests.get(url).json()
    return int(res["items"][0]["statistics"]["viewCount"])

def track(chat_id, video_id):
    last = None

    while True:
        try:
            views = get_views(video_id)
            now = datetime.now().strftime("%H:%M:%S")
            gain = 0 if last is None else views - last

            msg = f"""📊 YouTube Tracker

⏰ {now}
👀 Views: {views}
📈 Gain (5min): {gain}
"""

            send_msg(chat_id, msg)
            last = views

            time.sleep(300)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)

def handle_updates():
    offset = None

    while True:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?timeout=100&offset={offset}"
        res = requests.get(url).json()

        for update in res.get("result", []):
            offset = update["update_id"] + 1

            msg = update.get("message", {})
            text = msg.get("text", "")
            chat_id = msg["chat"]["id"]

            if text.startswith("/track"):
                try:
                    video_id = text.split(" ")[1]
                    send_msg(chat_id, "✅ Tracking started...")
                    threading.Thread(target=track, args=(chat_id, video_id)).start()
                except:
                    send_msg(chat_id, "❌ Send like: /track VIDEO_ID")

# ===== RUN =====
threading.Thread(target=run_web).start()
handle_updates()
