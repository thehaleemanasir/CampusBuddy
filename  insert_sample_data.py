

from database import mental_health_collection

mental_health_collection.insert_many([
    {"category": "emergency", "name": "Samaritans Ireland", "phone": "116 123", "website": "https://www.samaritans.org/ireland/samaritans-ireland/"},
    {"category": "self_help", "title": "Mental Health Ireland - Get Support", "link": "https://www.mentalhealthireland.ie/get-support/"},
    {"category": "video", "title": "Stress Management", "link": "https://www.youtube.com/embed/example1"}
])
