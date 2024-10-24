import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
from openai import AssistantEventHandler
from typing_extensions import override

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# EventHandler to handle the streaming response
class StreamlitEventHandler(AssistantEventHandler):
    def __init__(self, message_placeholder):
        super().__init__()
        self.message_placeholder = message_placeholder
        self.full_text = ""

    @override
    def on_text_delta(self, delta, snapshot):
        self.full_text += delta.value
        self.message_placeholder.markdown(self.full_text)

def main():
    st.title("Chat with Assistants")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    model = st.selectbox("Choose an Assistant", [
        "asst_IDB3oop3AS2Aoe5dZsjlvsak",
        "asst_xMMUIRQFfQmZCI30ifkvkGHf"
    ])

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.chat_message("user").markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )

        with st.chat_message("assistant"):
            message_placeholder = st.empty()  # Placeholder for streaming updates

            # Stream the assistant response
            event_handler = StreamlitEventHandler(message_placeholder)
            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=model,  # Use the selected assistant
                event_handler=event_handler,
            ) as stream:
                stream.until_done()

        # Save the full assistant response
        st.session_state.messages.append({"role": "assistant", "content": event_handler.full_text})


if __name__ == "__main__":
    main()
