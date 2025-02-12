import datetime
import json
import openai
from flask import Flask, render_template, request, jsonify, redirect
import os
from pymongo import MongoClient

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the JSON file
json_file_path = os.path.join(BASE_DIR, "campus_locations.json")

# Load the JSON file
with open(json_file_path) as f:
    campus_data = json.load(f)
app = Flask(__name__)

# MongoDB Connection
client = MongoClient(
    "mongodb+srv://k00267199:Haleema786@cluster0.atqsj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Update with your MongoDB URI
db = client['campus_buddy']
societies_collection = db['societies']
campuses_collection = db['campuses']
joined_collection = db['joined_societies']
chat_history_collection = db['chats_history']
socketTimeoutMS = 30000,
connectTimeoutMS = 30000

# Add your OpenAI API key


@app.route('/')
def homepage():
    return render_template('homepage.html')


@app.route('/society_club')
def society_club():
    # Fetch all campuses for the dropdown
    campuses = list(campuses_collection.find({}, {"_id": 0, "name": 1}))

    # Fetch joined societies
    joined_societies = list(joined_collection.find({}, {"_id": 0}))

    return render_template(
        'society_club.html',
        campuses=campuses,
        joined_societies=joined_societies
    )
@app.route('/join_society', methods=['GET', 'POST'])
def join_society():
    if request.method == 'POST':
        try:
            # Get form values safely
            campus = request.form.get('campus')
            society = request.form.get('society')
            contact_by_email = 'contactByEmail' in request.form  # Checkbox value

            # Validate form inputs
            if not campus or not society:
                return "Campus and society selection are required.", 400

            # Insert into the database
            joined_collection.insert_one({
                'campus': campus,
                'society': society,
                'contact_by_email': contact_by_email
            })

            return redirect('/society_club')
        except Exception as e:
            print("Error during form submission:", str(e))
            return "An error occurred. Check server logs.", 500

    # For GET requests, load the form
    campus_filter = request.args.get('campus', '')
    campuses = list(campuses_collection.find({}, {"_id": 0, "name": 1}))
    societies = []

    if campus_filter:
        societies = list(societies_collection.find({"campus": campus_filter}, {"_id": 0, "name": 1}))

    return render_template(
        'join_society.html',
        campuses=campuses,
        societies=societies,
        selected_campus=campus_filter
    )

@app.route('/societies_list', methods=['GET'])
def societies_list():
    try:
        # Fetch all campuses for the dropdown
        campuses = list(campuses_collection.find({}, {"_id": 0, "name": 1, "location": 1}))
        print("Campuses fetched:", campuses)

        # Fetch societies filtered by campus if selected
        campus_filter = request.args.get('campus', '')
        print("Campus filter:", campus_filter)

        if campus_filter:
            societies = list(societies_collection.find({"campus": campus_filter}, {"_id": 0}))
            print("Filtered societies:", societies)
        else:
            societies = list(societies_collection.find({}, {"_id": 0}))
            print("All societies:", societies)

        return render_template(
            'societies_list.html',
            campuses=campuses,
            societies=societies,
            selected_campus=campus_filter
        )
    except Exception as e:
        print("Error:", str(e))
        return "An error occurred. Check server logs.", 500


@app.route('/academic-support')
def academic_support():
    return render_template('academic_support.html')


@app.route('/mental-health')
def mental_health():
    return render_template('mental_health.html')


@app.route('/events')
def events():
    return render_template('events.html')


@app.route('/social-networking')
def social_networking():
    return render_template('social_networking.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/location', methods=['GET'])
def get_location():
    campus = request.args.get("campus", "").capitalize()
    query = request.args.get("query", "").title()

    if campus in campus_data:
        if query in campus_data[campus]["General"]:
            return jsonify(campus_data[campus]["General"][query])
        elif query in campus_data[campus]["Floors"]:
            return jsonify(campus_data[campus]["Floors"][query])
        else:
            return jsonify({"error": "Location not found"}), 404
    return jsonify({"error": "Campus not found"}), 404


@app.route('/map')
def map_page():
    return render_template('map.html')


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()

    if not question:
        return redirect("/chatbot")

    try:
        # Generate response from OpenAI
        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for TUS societies and clubs."},
                {"role": "user", "content": question}
            ],
            max_tokens=100,
            temperature=0.7
        )
        response = openai_response['choices'][0]['message']['content'].strip()

        # Save chat history
        chat_history_collection.insert_one({
            "sender": "user",
            "message": question,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        chat_history_collection.insert_one({
            "sender": "bot",
            "message": response,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return redirect("/chatbot")

    except Exception as e:
        print(f"Error: {e}")
        return redirect("/chatbot")


@app.route("/chatbot")
def chatbot():
    chat_history = list(chat_history_collection.find({}, {"_id": 0}))
    return render_template("chatbot.html", chat_history=chat_history)


def get_chat_history():
    """Retrieve the last 10 chat entries from MongoDB."""
    return list(chat_history_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(10))

def save_chat(user_query, bot_response):
    """Save the user query and bot response to MongoDB."""
    chat_history_collection.insert_one({
        "user_query": user_query,
        "bot_response": bot_response,
        "timestamp": datetime.datetime.utcnow()  # Store timestamp in UTC
    })


if __name__ == "__main__":
    app.run(debug=True)
