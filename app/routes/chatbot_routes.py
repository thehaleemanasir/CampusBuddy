import json
import requests
from flask import Blueprint, request, jsonify
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import os
import openai
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import re
from flask import session
import traceback

from app.routes.decorators import roles_required
from database import chat_history_collection, canteen_facilities_collection, canteen_menu_collection
from datetime import datetime


chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")


openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

with open("data/links.json", "r", encoding="utf-8") as f:
    all_links = json.load(f)

link_texts = [entry["title"] + " " + " ".join(entry.get("keywords", [])) for entry in all_links]
link_embeddings = model.encode(link_texts, convert_to_tensor=True)

mental_health_intents = [
    "I feel anxious",
    "I’m depressed",
    "I'm stressed about exams",
    "I feel overwhelmed",
    "Can you help me with meditation?",
    "I'm panicking",
    "Tips for exam stress",
    "I can't focus",
    "I feel burnt out",
    "My mind is racing",
    "I can’t think straight",
    "I’m losing it",
    "I hate this semester",
    "Everything is too much",
    "burnt out af",
    "nothing is helping me",
    "I just want to cry",
    "physical activity",
    "benefits of exercise",
    "how exercise helps stress",
    "movement and wellbeing",
    "physical exercise and anxiety",
    "fitness for burnout",
    "exercise helps mental health",
    "I need a breathing video",
    "breathing exercise",
    "deep breathing help",
    "how to calm down",
    "guided breathing",
    "mindful breathing",
    "breathing for anxiety",
    "help me breathe"

]

intent_embeddings = model.encode(mental_health_intents, convert_to_tensor=True)


# --- Helper Functions ---

def ocr_pdf_search(query):
    pdf_path = "app/static/resources/student_wellbeing_guide.pdf"
    text_content = ""

    try:
        with fitz.open(pdf_path) as doc:
            for page_num in range(min(3, len(doc))):  # First 3 pages
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text_content += pytesseract.image_to_string(img) + "\n"

        # Search the OCR'd text for best matching paragraph
        paragraphs = [p.strip() for p in text_content.split("\n\n") if len(p.strip()) > 50]
        para_embeddings = model.encode(paragraphs, convert_to_tensor=True)
        query_embedding = model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_embedding, para_embeddings)[0]
        best_index = scores.argmax().item()
        best_score = scores[best_index].item()

        return paragraphs[best_index] if best_score > 0.3 else None

    except Exception as e:
        print("OCR Error:", e)
        return None

def extract_text_and_links_from_pdf(query):
    pdf_path = "app/static/resources/student_wellbeing_guide.pdf"
    quote = None
    links = []

    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text = page.get_text()
                if query.lower() in text.lower():
                    for para in text.split("\n\n"):
                        if query.lower() in para.lower() and len(para.strip()) > 40:
                            quote = para.strip()
                    page_links = re.findall(r'(https?://[\S]+)', text)
                    links.extend(page_links)

        filtered_links = [link for link in links if any(kw in link.lower() for kw in ["youtube", "meditation", "mindful", "breathe", "togetherall", "50808"])]

        return quote, filtered_links[0] if filtered_links else None

    except Exception as e:
        print("❌ PDF text+link extract error:", e)
        return None, None


def is_emergency_contact_query(query):
    keywords = ["emergency contact", "emergency contacts", "urgent help", "crisis number", "who do I call", "in an emergency"]
    return any(k in query.lower() for k in keywords)

def is_mental_health_query_nlp(query):
    query_embedding = model.encode(query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, intent_embeddings)[0]
    top_score = cosine_scores.max().item()
    return top_score > 0.35

def is_faq_query(query):
    faq_keywords = ["how", "what", "can i", "when", "where", "faq", "apply", "eligibility", "who", "do i need"]
    return any(word in query.lower() for word in faq_keywords)

def find_best_link_semantic(query):
    query_embedding = model.encode(query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, link_embeddings)[0]
    best_index = cosine_scores.argmax().item()
    best_score = cosine_scores[best_index].item()
    if best_score >= 0.4:
        return all_links[best_index]
    return None

def scrape_faq_answer(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        content = soup.find('main') or soup.find('article') or soup
        for p in content.find_all("p"):
            text = p.get_text(strip=True)
            if text and len(text) > 40:
                return text
    except Exception as e:
        print("Scraping failed:", e)
    return None

def search_pdf_for_answer(query):
    pdf_path = "app/static/resources/student_wellbeing_guide.pdf"
    try:
        with fitz.open(pdf_path) as doc:
            full_text = ""
            for page in doc:
                full_text += page.get_text()

        paragraphs = [p.strip() for p in full_text.split("\n") if len(p.strip()) > 50]

        para_embeddings = model.encode(paragraphs, convert_to_tensor=True)
        query_embedding = model.encode(query, convert_to_tensor=True)

        cosine_scores = util.cos_sim(query_embedding, para_embeddings)[0]
        best_index = cosine_scores.argmax().item()
        best_score = cosine_scores[best_index].item()

        if best_score > 0.3:
            return paragraphs[best_index].strip()
        else:
            return None

    except Exception as e:
        return None

def is_canteen_query(user_input):
    keywords = ['canteen', 'menu', 'food', 'lunch', 'starbucks', 'cafe', 'outlet', 'available']
    return any(kw in user_input.lower() for kw in keywords)


def extract_campus_and_outlet(user_input, known_campuses, known_outlets):
    found_campus = None
    found_outlet = None
    for campus in known_campuses:
        if campus.lower() in user_input.lower():
            found_campus = campus
            break
    for outlet in known_outlets:
        if outlet.lower() in user_input.lower():
            found_outlet = outlet
            break
    return found_campus, found_outlet

def handle_canteen_query(user_input):

    dietary_tags = ["halal", "vegetarian", "vegan", "gluten-free"]
    context = session.get("canteen_context", {})
    user_input_lower = user_input.lower().strip()

    if any(word in user_input_lower for word in ["menu", "canteen", "food"]):
        context = {}

    known_campuses = canteen_facilities_collection.distinct("campus")

    for campus in known_campuses:
        if campus.lower() == user_input_lower or campus.lower() in user_input_lower:
            context["campus"] = campus
            break

    if "campus" not in context:
        session["canteen_context"] = context
        campus_list = ", ".join(known_campuses)
        return f"📍 Which campus are you in? Available campuses: {campus_list}"

    campus_doc = canteen_facilities_collection.find_one({"campus": context["campus"]})
    outlet_names = [o["name"] for o in campus_doc.get("outlets", [])] if campus_doc else []

    for outlet in outlet_names:
        if outlet.lower().replace(" ", "") in user_input_lower.replace(" ", ""):
            context["outlet"] = outlet
            break

    if "outlet" not in context:
        session["canteen_context"] = context
        return f"🍽️ Which outlet would you like to check at {context['campus']}? ➡️ {', '.join(outlet_names)}"

    for tag in dietary_tags:
        if tag in user_input_lower:
            context["diet"] = tag
            break

    session["canteen_context"] = context

    query = {
        "campus": context["campus"],
        "outlet": context["outlet"],
        "archived": False
    }
    if "diet" in context:
        query["dietary"] = {"$regex": context["diet"], "$options": "i"}

    menu_items = list(canteen_menu_collection.find(query, {"_id": 0, "item_name": 1, "price": 1, "dietary": 1}))

    if not menu_items:
        session.pop("canteen_context", None)
        return f"❌ No menu items found for {context['outlet']} at {context['campus']}."

    response = f"📋 Menu at <b>{context['outlet']}</b>, <b>{context['campus']}</b>:<br>"
    for item in menu_items:
        dietary = f" ({item.get('dietary')})" if item.get("dietary") else ""
        response += f"• {item['item_name']} – €{item['price']:.2f}{dietary}<br>"

    session.pop("canteen_context", None)
    return response


def is_canteen_followup(query):
    campuses = canteen_facilities_collection.distinct("campus")
    return query.lower() in [camp.lower() for camp in campuses]



# --- Main Route ---
def get_mental_health_reply(user_query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You're a warm, non-judgmental mental health companion for university students. "
                    "Be gentle and conversational, especially if someone expresses distress. "
                    "Let them know it's okay to talk more if they want to. Use phrases like 'Would you like to share more about that?' or 'I'm here to listen if you feel like talking.' "
                    "Do not rush to fix — just listen, validate, and support. "
                    "At the end, say: 'You are not alone, and support is available.'"

                },
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            temperature=0.7,
            max_tokens=200
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        traceback.print_exc()
        return "I'm here for you, but something went wrong while generating a response. Please try again later."



@chatbot_bp.route("", methods=["POST"])
@roles_required('student', 'staff')
def chatbot():
    data = request.json
    query = data.get("query", "").strip()

    if is_canteen_query(query) or session.get("canteen_context") or is_canteen_followup(query):
        try:
            return jsonify({"reply": handle_canteen_query(query)})
        except Exception as e:
            print("❌ Canteen chatbot error:", e)
            return jsonify({"reply": "⚠️ Something went wrong with the menu system. Try again later."})

    recent_log = chat_history_collection.find_one({
        "question": {"$regex": re.escape(query), "$options": "i"},
        "edited": True
    })

    if "exam" in query.lower() and any(word in query.lower() for word in
                                       ["timetable", "schedule", "date", "time", "when", "where", "exam office"]):
        return jsonify({
            "reply": "📚 For exam timetables and related queries, please check the Exams Office portal: "
                     "<a href='https://tus.ie/exams/' target='_blank'>TUS Exam Info</a> or contact exams@tus.ie"
        })

    if recent_log:
        return jsonify({"reply": recent_log["response"]})
    manual_entry = chat_history_collection.find_one({
        "question": query.lower().strip(),
        "edited": True
    })

    if manual_entry:
        return jsonify({"reply": manual_entry["response"]})

    polite_end_phrases = [
        "no i can't", "i can't share", "never mind", "i'm fine", "no thank you",
        "i'm okay", "i feel better", "thank you", "thanks", "bye", "not now", "stop", "okay bye", "no"
    ]
    query_clean = query.lower()

    if any(phrase in query_clean for phrase in polite_end_phrases):
        if session.get("in_support_chat"):
            session.pop("in_support_chat", None)
        return jsonify({
            "reply": "No Worries 💛 I'm always here whenever you want to talk again. Take care!"
        })

    if not query:
        return jsonify({"reply": "❗ Please enter a question."})

    try:
        if is_emergency_contact_query(query):
            emergency_info = (
                "📞 <b>In case of an emergency, contact:</b><br><br>"
                "📍 <b>TUS Counselling Emergency Support:</b> 061-293000<br>"
                "📍 <b>HSE Mental Health Services:</b> 1800 111 888<br>"
                "📍 <b>Emergency Services (Ambulance / Garda):</b> 999 or 112<br><br>"
                "🧠 <i>You are not alone. Help is always available.</i><br><br>"
                "📄 <a href='/static/resources/student_wellbeing_guide.pdf' target='_blank'>View Full Wellbeing Guide</a>"
            )
            return jsonify({"reply": emergency_info})

        if query.lower() in ["i feel good", "i feel okay"]:
            session.pop("in_support_chat", None)
            return jsonify({
                "reply": "Thank you for checking in 🌈 I'm really glad to hear that. I'm here anytime you need support!"
            })

        if query.lower() in ["i feel low"]:
            session['in_support_chat'] = True
            ai_reply = get_mental_health_reply("I'm feeling low")
            ai_reply += "<br><br>💬 I'm here for you. Would you like to share more about how you're feeling?"
            disclaimer = "⚠️ This is not a replacement for professional help. If you're in crisis, please contact campus counselling or emergency services."

            return jsonify({
                "reply": f"{ai_reply}<br><br>{disclaimer}"
            })
        if is_mental_health_query_nlp(query):
            polite_end_phrases = [
                "no i can't", "i can't share", "never mind", "i'm fine", "no thank you",
                "i'm okay", "i feel better", "thank you", "bye", "not now", "stop", "okay bye", "bye", "no"
            ]
            if any(phrase in query.lower() for phrase in polite_end_phrases):
                session.pop("in_support_chat", None)
                return jsonify({
                    "reply": "No Worries💛 I'm always here whenever you want to talk again. Take care!"
                })

            in_session = session.get("in_support_chat", False)
            if not in_session:
                session['in_support_chat'] = True

            pdf_answer = search_pdf_for_answer(query)
            if not pdf_answer:
                pdf_answer = ocr_pdf_search(query)

            hardcoded_links = {
                "breathing": "https://youtu.be/n6RbW2LtdFs",
                "meditation": "https://youtu.be/j4-dMVI9okU",
                "guided meditation": "https://youtu.be/j4-dMVI9okU",
                "mindfulness": "https://youtu.be/j4-dMVI9okU",
                "togetherall": "https://togetherall.com/en-ie/",
                "text": "https://text50808.ie/"
            }

            pdf_link = None
            for keyword, link in hardcoded_links.items():
                if keyword in query.lower():
                    pdf_link = link
                    break

            ai_reply = get_mental_health_reply(query)

            log_flag = (
                    "feedback" in query.lower() or
                    "sorry" in ai_reply.lower() or
                    "[unknown]" in ai_reply.lower()
            )

            if log_flag:
                chat_history_collection.insert_one({
                    "user_email": session.get("email", "guest"),
                    "question": query,
                    "response": ai_reply,
                    "timestamp": datetime.utcnow()
                })
            if pdf_link:
                if "[link to video]" in ai_reply:
                    ai_reply = ai_reply.replace("[link to video]",
                                                f"<a href='{pdf_link}' target='_blank'>Watch the video</a>")
                else:
                    ai_reply += f"<br><br>🎥 <a href='{pdf_link}' target='_blank'>Watch a related video</a>"

            if pdf_answer:
                ai_reply += f"<br><br><b>From the wellbeing guide:</b><br>{pdf_answer}"

            ai_reply += "<br><br>📄 <a href='/static/resources/student_wellbeing_guide.pdf' target='_blank'>View Full Wellbeing Guide</a>"

            if in_session:
                ai_reply += "<br><br>💬 I’m still here if you want to keep talking. No pressure."

            disclaimer = "⚠️ This is not a replacement for professional help. If you're in crisis, please contact campus counselling or emergency services."

            followup_buttons = """
            <br><br><b>💡 Need more help?</b><br>
            <button class='chip' onclick="sendQuickMessage('Mindfulness tips')">🧘 Mindfulness Tips</button>
            <button class='chip' onclick="sendQuickMessage('How to deal with exam stress?')">📚 Exam Stress Relief</button>
            <button class='chip' onclick="sendQuickMessage('How do I book a counselling session?')">📝 Book a Counselling Session</button>
            <button class='chip' onclick="sendQuickMessage('What are the emergency contacts?')">📞 Crisis Support</button>
            
            
            <br><br><b>🌈 How are you feeling today?</b><br>
            <button class='chip' onclick="sendQuickMessage('I feel good')">😌 Good</button>
            <button class='chip' onclick="sendQuickMessage('I feel okay')">😐 Okay</button>
            <button class='chip' onclick="sendQuickMessage('I feel low')">😢 Low</button>
            """

            return jsonify({
                "reply": f"{ai_reply}<br><br>{disclaimer}{followup_buttons}"
            })

        best_match = find_best_link_semantic(query)

        if best_match:
            if is_faq_query(query):
                answer = scrape_faq_answer(best_match["url"])
                if answer:
                    return jsonify({
                        "reply": f"{answer}<br><br>🔗 <a href='{best_match['url']}' target='_blank'>{best_match['title']}</a>"
                    })

            return jsonify({
                "reply": f"Here’s what I found:<br><br>🔗 <a href='{best_match['url']}' target='_blank'>{best_match['title']}</a>"
            })

        response = "⚠️ Sorry, I couldn't find anything. Try rephrasing your question."

        if is_mental_health_query_nlp(query):
            ai_reply = get_mental_health_reply(query)

            log_flag = (
                    "feedback" in query.lower() or
                    "sorry" in ai_reply.lower() or
                    "[unknown]" in ai_reply.lower()
            )

            if log_flag:
                chat_history_collection.insert_one({
                    "user_email": session.get("email", "guest"),
                    "question": query,
                    "response": ai_reply,
                    "timestamp": datetime.utcnow()
                })

            return jsonify({"reply": ai_reply})


        response = "⚠️ Sorry, I couldn't find anything. Try rephrasing your question."

        log_flag = (
                "feedback" in query.lower() or
                "sorry" in response.lower()
        )

        if log_flag:
            chat_history_collection.insert_one({
                "user_email": session.get("email", "guest"),
                "question": query,
                "response": response,
                "timestamp": datetime.utcnow()
            })

        return jsonify({"reply": response})

    except Exception as e:
        print("❌ Chatbot Error:", e)
        return jsonify({"reply": "⚠️ Something went wrong, but I'm still learning. Please try again."})
