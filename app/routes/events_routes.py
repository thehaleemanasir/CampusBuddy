from flask import Blueprint, request, jsonify, render_template
from flask_mail import Mail, Message
from database import events_collection
from bson.objectid import ObjectId
import datetime

events_bp = Blueprint('events', __name__)

# Flask-Mail Configuration
from flask import Flask

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
mail = Mail(app)


#  Fetch events from MongoDB for FullCalendar
@events_bp.route('/get-events')
def get_events():
    events = list(events_collection.find({}, {"_id": 1, "title": 1, "date": 1}))
    for event in events:
        event["_id"] = str(event["_id"])
        event["start"] = event["date"]
    return jsonify(events)


#  Add a new event to MongoDB
@events_bp.route('/add-event', methods=['POST'])
def add_event():
    data = request.json
    event_id = events_collection.insert_one({
        "title": data["title"],
        "date": data["date"],
        "email": data["email"]
    }).inserted_id
    return jsonify({"success": True, "id": str(event_id)})


#  Delete an event from MongoDB
@events_bp.route('/delete-event', methods=['POST'])
def delete_event():
    data = request.json
    event_id = data.get("id")

    if not event_id:
        return jsonify({"success": False, "message": "No event ID provided"})

    result = events_collection.delete_one({"_id": ObjectId(event_id)})
    return jsonify({"success": result.deleted_count > 0})

#  Send email reminder for an event
@events_bp.route('/send-email-reminder', methods=['POST'])
def send_email_reminder():
    data = request.json
    event_title = data.get('title')
    event_date = data.get('date')
    user_email = data.get('email')

    if not user_email:
        return jsonify({"success": False, "message": "User email not found"})

    # Format event time
    event_time = datetime.datetime.strptime(event_date, "%Y-%m-%dT%H:%M")

    # Send email reminder
    msg = Message(f"⏰ Event Reminder: {event_title}",
                  sender="your-email@gmail.com",
                  recipients=[user_email])
    msg.body = f"📅 Reminder: {event_title} is happening on {event_time.strftime('%A, %B %d, %Y at %I:%M %p')}.\n\nDon't forget to attend!"

    try:
        mail.send(msg)
        print(f"✅ Email sent successfully to: {user_email}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return jsonify({"success": False, "error": str(e)})



@events_bp.route("/calendar")
def show_calendar():
    return render_template("calender.html")


