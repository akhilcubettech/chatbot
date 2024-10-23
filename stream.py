import streamlit as st
import requests
import os

# Set your API endpoint
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY =  os.getenv("OPENAI_API_KEY")

def query_chatbot(message, model):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": message}]
    }
    response = requests.post(API_URL, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

def main():
    st.title("Chatbot Interface")
    model = st.selectbox("Choose a Bot", ["gpt-3.5-turbo", "gpt-4"])
    user_input = st.text_input("You: ", "")

    if st.button("Send"):
        if user_input:
            response = query_chatbot(user_input, model)
            st.text_area("Bot:", value=response, height=200, max_chars=None, key=None)

if __name__ == "__main__":
    main()