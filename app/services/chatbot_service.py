import openai  # ✅ Correct Import for OpenAI API
import os

# Load API Key (Ensure you have set your API Key here)
OPENAI_API_KEY  = ("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")

def generate_chat_response(question):
    try:
        openai.api_key = OPENAI_API_KEY

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": question}],
            max_tokens=150
        )

        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"