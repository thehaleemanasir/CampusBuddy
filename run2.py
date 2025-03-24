import json
import os
from collections import defaultdict
from fuzzywuzzy import process

# Folder containing all FAQ JSON files
FAQ_FOLDER = "faq"

# Dictionary to store loaded FAQ data
faq_data = {}


# Function to generate keywords from filenames
def generate_keywords_from_filename(filename):
    """Generate keywords from a filename by splitting on common delimiters."""
    name = filename.replace(".json", "")
    keywords = name.replace("_", " ").replace("-", " ").split()
    keywords = [word.lower() for word in keywords]
    return keywords


# Function to dynamically create file_mapping
def create_file_mapping():
    """Create a file_mapping dictionary dynamically based on filenames."""
    file_mapping = defaultdict(list)
    for file in os.listdir(FAQ_FOLDER):
        if file.endswith(".json"):
            keywords = generate_keywords_from_filename(file)
            for keyword in keywords:
                file_mapping[keyword].append(file)
    return file_mapping


# Function to load all JSON files at startup
def load_all_faqs():
    """Loads all FAQ JSON files from the folder into a dictionary."""
    global faq_data
    faq_data.clear()  # Clear previous data

    for file in os.listdir(FAQ_FOLDER):
        if file.endswith(".json"):
            file_path = os.path.join(FAQ_FOLDER, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    faq_data[file] = data
            except json.JSONDecodeError:
                print(f"Error: Could not parse {file}")
            except FileNotFoundError:
                print(f"Error: {file} not found.")


# Load all FAQs at the start
load_all_faqs()

# Create the file_mapping dynamically
file_mapping = create_file_mapping()


# Function to find an answer based on user query
def get_answer(user_query):
    """Searches all loaded FAQs for a relevant answer using fuzzy matching."""
    user_query = user_query.lower()

    # Check for common queries like email, phone, etc.
    if "email" in user_query:
        return "You can contact the international office at international.office@example.com."

    # Determine which JSON file(s) to search based on keywords
    target_files = set()
    for keyword, files in file_mapping.items():
        if keyword in user_query:
            target_files.update(files)

    # If specific files are found, search only in those files
    if target_files:
        for file in target_files:
            if file in faq_data:
                data = faq_data[file]
                for key in data:
                    for item in data[key]:
                        if isinstance(item, dict) and "question" in item and "answer" in item:
                            # Use fuzzy matching to compare the user's query with the question
                            match_ratio = process.extractOne(user_query, [item["question"].lower()])
                            if match_ratio[1] > 70:  # Adjust the threshold as needed
                                return item["answer"]

    # If no specific files are found, search through all files
    for file_name, data in faq_data.items():
        for key in data:
            for item in data[key]:
                if isinstance(item, dict) and "question" in item and "answer" in item:
                    match_ratio = process.extractOne(user_query, [item["question"].lower()])
                    if match_ratio[1] > 70:  # Adjust the threshold as needed
                        return item["answer"]

    # If no match is found, suggest related topics
    related_topics = set()
    for keyword in user_query.split():
        if keyword in file_mapping:
            related_topics.update(file_mapping[keyword])

    if related_topics:
        return f"I'm not sure how to answer that. Here are some related topics you might find useful: {', '.join(related_topics)}"
    else:
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