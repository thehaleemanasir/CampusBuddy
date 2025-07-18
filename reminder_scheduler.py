from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from bson import ObjectId
from database import calendar_events_collection, users_collection
from extensions import socketio

def start_reminder_scheduler():
    scheduler = BackgroundScheduler()

    @scheduler.scheduled_job('interval', minutes=1)
    def send_reminders():
        now = datetime.utcnow()

        timings = [
            {"label": "🕒 30 mins before", "delta": 30, "field": "notified_30"},
            {"label": "🔔 10 mins before", "delta": 10, "field": "notified_10"},
            {"label": "⏱ 5 mins before", "delta": 5, "field": "notified_5"}
        ]

        for timing in timings:
            target_time = now + timedelta(minutes=timing["delta"])
            upcoming = calendar_events_collection.find({
                "start": {"$gte": now, "$lt": target_time},
                timing["field"]: {"$ne": True}
            })

            for event in upcoming:
                user = users_collection.find_one({"_id": ObjectId(event["user_id"])})
                if not user:
                    continue

                message = f"{timing['label']}: You have '{event['title']}' at {event['start'].strftime('%H:%M')}!"
                socketio.emit("new_event", {
                    "message": message,
                    "id": str(event["_id"])
                })

                calendar_events_collection.update_one(
                    {"_id": event["_id"]},
                    {"$set": {timing["field"]: True}}
                )

        in_15_min = now + timedelta(minutes=15)
        ending_soon = calendar_events_collection.find({
            "end": {"$gte": now, "$lt": in_15_min},
            "end_notified": {"$ne": True}
        })

        for event in ending_soon:
            user = users_collection.find_one({"_id": ObjectId(event["user_id"])})
            if not user:
                continue

            message = f"⌛ '{event['title']}' is ending at {event['end'].strftime('%H:%M')}!"
            socketio.emit("new_event", {
                "message": message,
                "id": str(event["_id"])
            })
            calendar_events_collection.update_one(
                {"_id": event["_id"]},
                {"$set": {"end_notified": True}}
            )

    scheduler.start()




