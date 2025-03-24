import json
import requests
from flask import Blueprint, request, jsonify
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")

# Load Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load links
with open("links.json", "r", encoding="utf-8") as f:
    all_links = json.load(f)

# Prepare text for embeddings
link_texts = [entry["title"] + " " + " ".join(entry.get("keywords", [])) for entry in all_links]
link_embeddings = model.encode(link_texts, convert_to_tensor=True)

# --- Helper Functions ---

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

# --- Main Route ---

@chatbot_bp.route("", methods=["POST"])
def chatbot():
    data = request.json
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"reply": "❗ Please enter a question."})

    best_match = find_best_link_semantic(query)

    if best_match:
        if is_faq_query(query):
            answer = scrape_faq_answer(best_match["url"])
            if answer:
                return jsonify({
                    "reply": f"{answer}\n\n🔗 <a href='{best_match['url']}' target='_blank'>{best_match['title']}</a>"
                })

        return jsonify({
            "reply": f"Here’s what I found:\n🔗 <a href='{best_match['url']}' target='_blank'>{best_match['title']}</a>"
        })

    return jsonify({"reply": "⚠️ Sorry, I couldn't find anything. Try rephrasing your question."})
