from http.client import responses

import streamlit as st
import requests
import os
from openai import OpenAI
from uuid import uuid4 as uid


client = OpenAI()

API_URL = "https://api.openai.com/v1/assistants/chat"
API_KEY = os.getenv("OPENAI_API_KEY")


# def query_chatbot(messages, model):
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "OpenAI-Beta": "assistants=v2",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "model": model,
#         "messages": messages
#     }
#     response = requests.post(API_URL, headers=headers, json=data)
#
#     if response.status_code != 200:
#         return "Error: " + response.text
#
#     return response.json()['choices'][0]['message']['content']


def main():
    st.title("Chatbot Interface")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    model = st.selectbox("Choose a Bot", ["gpt-3.5-turbo", "gpt-4", "asst_IDB3oop3AS2Aoe5dZsjlvsak"])

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.chat_message("user").markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        # response = query_chatbot(st.session_state.messages, model)
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=str(prompt)
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=model,
        )
        response = None
        if run.status == 'completed':
            response = client.beta.threads.messages.list(
                thread_id=thread.id
            )

        else:
            response=run.status

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
