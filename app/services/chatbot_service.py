import openai

def generate_chat_response(question):
    try:
        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for TUS societies and clubs."},
                {"role": "user", "content": question}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return openai_response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, an error occurred while fetching a response."
