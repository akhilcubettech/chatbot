# import streamlit as st
# import requests
# import os
#
# API_URL = "https://api.openai.com/v1/chat/completions"
# API_KEY =  os.getenv("OPENAI_API_KEY")
#
# def query_chatbot(message, model):
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "model": model,
#         "messages": [{"role": "user", "content": message}]
#     }
#     response = requests.post(API_URL, headers=headers, json=data)
#     return response.json()['choices'][0]['message']['content']
#
# def main():
#     st.title("Chatbot Interface")
#     model = st.selectbox("Choose a Bot", ["gpt-3.5-turbo", "gpt-4"])
#     user_input = st.text_input("You: ", "")
#
#     if st.button("Send"):
#         if user_input:
#             response = query_chatbot(user_input, model)
#             st.text_area("Bot:", value=response, height=200, max_chars=None, key=None)
#
# if __name__ == "__main__":
#     main()


import streamlit as st
import requests
import os
from uuid import uuid4 as uid

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

    if response.status_code != 200:
        return "Error: " + response.text

    return response.json()['choices'][0]['message']['content']


def main():
    st.title("Chatbot Interface")


    if "messages" not in st.session_state:
        st.session_state.messages = []


    model = st.selectbox("Choose a Bot", ["gpt-3.5-turbo", "gpt-4"])

    for message in st.session_state.messages:
        if message["role"] == "user":
            st.text(f'You: {message["content"]}')
            # st.text_area'("You:", value=message["content"], key=uid, disabled=True)
        else:
            st.text(f'Bot: {message["content"]}')
            # st.text_area("Bot:", value=message["content"], key=uid, disabled=True)

    user_input = st.text_input("Type your message:", "", key="user_input")

    if st.button("Send"):
        if user_input:

            st.session_state.messages.append({"role": "user", "content": user_input})

            response = query_chatbot(st.session_state.messages, model)


            st.session_state.messages.append({"role": "assistant", "content": response})

            st.session_state.user_input = ""


            st.rerun()


if __name__ == "__main__":
    main()
