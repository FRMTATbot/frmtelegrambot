from flask import Flask, request
import requests, time, threading
from datetime import datetime, timedelta

app = Flask(__name__)

BOT_TOKEN = '8124226038:AAEo8iGZujc7MQiGn2-Uz2w--Y4VH6orkiA'
GROUP_ID = '-4872254663'

# Store jobcard timers
jobcards = {}

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": GROUP_ID, "text": text}
    requests.post(url, data=data)

def schedule_reminders(veh_no, total_minutes):
    now = datetime.now()
    deadline = now + timedelta(minutes=total_minutes)
    jobcards[veh_no] = {"deadline": deadline, "closed": False}

    def reminder_loop():
        while datetime.now() < deadline and not jobcards[veh_no]["closed"]:
            remaining = deadline - datetime.now()
            mins = remaining.total_seconds() / 60

            if 89 < mins <= 91:
                send_message(f"⏰ 1 hour passed for {veh_no}")
            elif 30 < mins <= 31:
                send_message(f"⚠️ 30 minutes remaining for {veh_no}")
            elif 15 < mins <= 16:
                send_message(f"⚠️ 15 minutes remaining for {veh_no}")
            time.sleep(60)

        if not jobcards[veh_no]["closed"]:
            send_message(f"❌ Time's up for {veh_no}")

    threading.Thread(target=reminder_loop).start()

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        text = data["message"].get("text", "")
        if text.startswith("JC"):
            parts = text.split()
            veh_no = parts[1]
            if len(parts) == 2:
                send_message(f"✅ Jobcard {veh_no} started. 3 hours deadline.")
                schedule_reminders(veh_no, 180)
            elif len(parts) == 3:
                if parts[2].lower() == "close":
                    jobcards[veh_no]["closed"] = True
                    send_message(f"✅ Jobcard {veh_no} closed.")
                else:
                    try:
                        extra_time = float(parts[2])
                        total = 180 + int(extra_time * 60)
                        send_message(f"✅ Added {extra_time} hours to {veh_no}. New deadline in {total // 60} mins.")
                        schedule_reminders(veh_no, total)
                    except:
                        send_message("❌ Invalid extra time format.")
    return {"ok": True}
