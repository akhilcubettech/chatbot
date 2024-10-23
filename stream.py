import os

import streamlit as st
import requests

API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv("OPENAI_API_KEY")



def query_chatbot(messages, model):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages
    }
    response = requests.post(API_URL, headers=headers, json=data)

    # Handle errors
    if response.status_code != 200:
        return "Error: " + response.text

    return response.json()['choices'][0]['message']['content']


def main():
    st.title("Chatbot Interface")


    model = st.selectbox("Choose a Bot", ["gpt-3.5-turbo", "gpt-4"])  # Add custom models as needed


    if "messages" not in st.session_state:
        st.session_state.messages = []


    for message in st.session_state.messages:
        if message["role"] == "user":
            st.text_area("You:", value=message["content"], height=50, key=message["content"], disabled=True)
        else:
            st.text_area("Bot:", value=message["content"], height=50, key=message["content"], disabled=True)


    user_input = st.text_input("Type your message:", "")

    if st.button("Send"):
        if user_input:

            st.session_state.messages.append({"role": "user", "content": user_input})

            response = query_chatbot(st.session_state.messages, model)


            st.session_state.messages.append({"role": "assistant", "content": response})


            st.rerun()


if __name__ == "__main__":
    main()
