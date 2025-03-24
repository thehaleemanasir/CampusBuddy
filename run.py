import json
import os

# Folder containing all FAQ JSON files
FAQ_FOLDER = "faq"

# Dictionary to store loaded FAQ data
faq_data = {}

# Function to load all JSON files at startup
def load_all_faqs():
    """Loads all FAQ JSON files into a dictionary."""
    global faq_data
    faq_data.clear()

    for file in os.listdir(FAQ_FOLDER):
        if file.endswith(".json"):
            file_path = os.path.join(FAQ_FOLDER, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    faq_data[file] = data  # Store JSON data with filename as key
            except json.JSONDecodeError:
                print(f"Error: Could not parse {file}")
            except FileNotFoundError:
                print(f"Error: {file} not found.")

# Load all FAQs at the start
load_all_faqs()

# Function to find an answer using partial matching
def get_answer(user_query):
    """Searches all loaded FAQs for the best answer using partial matching."""
    user_query = user_query.lower()  # Normalize user input

    # Store best match
    best_match = None
    best_match_score = 0

    # Loop through all JSON data files
    for file_name, data in faq_data.items():
        for key in data:  # Loop through categories in each JSON file
            for item in data[key]:  # Loop through individual FAQs
                if isinstance(item, dict) and "question" in item and "answer" in item:
                    question_text = item["question"].lower()

                    # Check if the user's query is in the stored question OR vice versa
                    match_score = sum(1 for word in user_query.split() if word in question_text)

                    if match_score > best_match_score:  # Update best match if score is higher
                        best_match_score = match_score
                        best_match = item["answer"]

    if best_match:
        return best_match  # Return the best matching answer

    return "I'm not sure how to answer that. Can you provide more details?"

# Chatbot loop
if __name__ == "__main__":
    print("Chatbot is ready! Type 'exit' to quit.")

    while True:
        user_input = input("Ask a question: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        response = get_answer(user_input)
        print("Chatbot:", response)

