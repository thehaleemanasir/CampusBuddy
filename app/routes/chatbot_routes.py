import datetime
from flask import Blueprint, render_template, request, redirect
from database import chat_history_collection
import openai
import os

# **HARD-CODE OpenAI API Key for Debugging (Replace with actual key)**
OPENAI_API_KEY = "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"

chatbot_bp = Blueprint('chatbot', __name__, template_folder="../templates")

@chatbot_bp.route("/chatbot")
def chatbot():
    chat_history = list(chat_history_collection.find({}, {"_id": 0}))
    return render_template("chatbot.html", chat_history=chat_history)

@chatbot_bp.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()

    if not question:
        return redirect("/chatbot")

    try:
        print(f"🔍 Received Question: {question}")  # Debugging

        # **Make a direct request to OpenAI API**
        openai.api_key = OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": question}]
        )

        bot_response = response["choices"][0]["message"]["content"]
        print(f" OpenAI Response: {bot_response}")  # Debugging

        # **Save chat history in MongoDB**
        chat_history_collection.insert_one({
            "sender": "user",
            "message": question,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        chat_history_collection.insert_one({
            "sender": "bot",
            "message": bot_response,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        print(f"Error in ask(): {e}")  # Debugging
        return "Error processing request", 500

    return redirect("/chatbot")
