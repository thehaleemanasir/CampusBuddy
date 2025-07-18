from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime, timedelta

from app.routes.decorators import roles_required
from database import calendar_events_collection
import logging
from functools import wraps
from extensions import socketio
calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def json_response(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            response = jsonify(result[0] if isinstance(result, tuple) else result)
            response.headers['Content-Type'] = 'application/json'
            if isinstance(result, tuple):
                response.status_code = result[1]
            return response
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return wrapper

@calendar_bp.route('/', endpoint='calendar')
@roles_required('student', 'staff', 'admin')
def calendar_home():
    return render_template("calendar.html")

@calendar_bp.route('/events', methods=['GET'])
@login_required
@json_response
def get_events():
    events = list(calendar_events_collection.find({
        'user_id': current_user.id
    }))

    formatted_events = []
    for event in events:
        formatted_events.append({
            'id': str(event['_id']),
            'title': event['title'],
            'start': event['start'].isoformat(),
            'end': event.get('end', '').isoformat() if event.get('end') else '',
            'description': event.get('description', ''),
            'color': event.get('color', '#3788d8')
        })

    return {'events': formatted_events}


@calendar_bp.route('/add', methods=['POST'])
@login_required
@json_response
def add_event():
    if not request.is_json:
        raise ValueError("Request must be JSON")

    data = request.get_json()
    if not data.get('title'):
        raise ValueError("Title is required")
    if not data.get('start'):
        raise ValueError("Start time is required")

    event = {
        'user_id': current_user.id,
        'title': data['title'],
        'start': datetime.fromisoformat(data['start']),
        'end': datetime.fromisoformat(data['end']) if data.get('end') else None,
        'description': data.get('description', ''),
        'color': data.get('color', '#3788d8'),
        'created_at': datetime.utcnow(),
        'notified': False
    }
    result = calendar_events_collection.insert_one(event)
    event['_id'] = str(result.inserted_id)

    socketio.emit('new_event', {
        'message': f"📅 Event added: {data['title']} at {data['start']}"
    })
    event['start'] = event['start'].isoformat()
    if event['end']:
        event['end'] = event['end'].isoformat()
    return {'message': 'Event added successfully', 'event': event}, 201


@calendar_bp.route('/update/<event_id>', methods=['PUT'])
@login_required
@json_response
def update_event(event_id):
    if not request.is_json:
        raise ValueError("Request must be JSON")

    data = request.get_json()

    update_fields = {}
    if 'title' in data:
        update_fields['title'] = data['title']
    if 'start' in data:
        update_fields['start'] = datetime.fromisoformat(data['start'])
    if 'end' in data:
        update_fields['end'] = datetime.fromisoformat(data['end']) if data['end'] else None
    if 'description' in data:
        update_fields['description'] = data['description']
    if 'color' in data:
        update_fields['color'] = data['color']

    result = calendar_events_collection.update_one(
        {'_id': ObjectId(event_id), 'user_id': current_user.id},
        {'$set': update_fields}
    )

    if result.matched_count == 0:
        raise ValueError("Event not found or not owned by user")

    return {'message': 'Event updated successfully'}


@calendar_bp.route('/delete/<event_id>', methods=['DELETE'])
@login_required
@json_response
def delete_event(event_id):
    result = calendar_events_collection.delete_one({
        '_id': ObjectId(event_id),
        'user_id': current_user.id
    })

    if result.deleted_count == 0:
        raise ValueError("Event not found or not owned by user")

    return {'message': 'Event deleted successfully'}


@calendar_bp.route('/reminders', methods=['GET'])
@login_required
def get_user_reminders():
    now = datetime.utcnow()
    in_1_hour = now + timedelta(hours=1)

    reminders = calendar_events_collection.find({
        "user_id": current_user.id,
        "start": {"$gte": now, "$lt": in_1_hour},
        "dismissed": {"$ne": True},
        "$or": [
            {"snoozed_until": {"$exists": False}},
            {"snoozed_until": {"$lte": now}}
        ]
    })

    return jsonify({
        "reminders": [{
            "id": str(r["_id"]),
            "title": r["title"],
            "time": r["start"].strftime('%H:%M'),
            "message": f"📌 {r['title']} at {r['start'].strftime('%H:%M')}"
        } for r in reminders]
    })
@calendar_bp.route('/dismiss/<event_id>', methods=['POST'])
@login_required
def dismiss_event(event_id):
    calendar_events_collection.update_one(
        {"_id": ObjectId(event_id), "user_id": current_user.id},
        {"$set": {"dismissed": True}}
    )
    return jsonify({"status": "ok"})

@calendar_bp.route('/snooze/<event_id>', methods=['POST'])
@login_required
def snooze_event(event_id):
    data = request.json
    minutes = data.get("minutes", 5)
    snooze_until = datetime.utcnow() + timedelta(minutes=minutes)

    calendar_events_collection.update_one(
        {"_id": ObjectId(event_id), "user_id": current_user.id},
        {"$set": {"snoozed_until": snooze_until}}
    )
    return jsonify({"status": "snoozed", "until": snooze_until})
