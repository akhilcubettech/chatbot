import tempfile
import streamlit as st
import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from openai import AssistantEventHandler
from typing_extensions import override

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
h_key = os.getenv("HUMANTIC_API_KEY")

class StreamlitEventHandler(AssistantEventHandler):
    def __init__(self, message_placeholder):
        super().__init__()
        self.message_placeholder = message_placeholder
        self.full_text = ""

    @override
    def on_event(self, event):
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id
            self.handle_requires_action(event.data, run_id, self.message_placeholder)

    def handle_requires_action(self, data, run_id, message_placeholder):
        tool_outputs = []
        for tool in data.required_action.submit_tool_outputs.tool_calls:
            arguments = json.loads(tool.function.arguments)
            if tool.function.name == "get_humantic_profile":
                linkedin_url = arguments.get("linkedin_url")
                if linkedin_url:
                    profile_data = get_humantic_profile(linkedin_url)
                    profile_data_str = json.dumps(profile_data)
                    tool_outputs.append({"tool_call_id": tool.id, "output": profile_data_str})
        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
        ) as stream:
            for text in stream.text_deltas:
                self.full_text += text
                self.message_placeholder.markdown(self.full_text)


def get_humantic_profile(linkedin_url):
    headers = {'Content-Type': 'application/json'}
    response = requests.get(f"https://api.humantic.ai/v1/user-profile?apikey={h_key}&id={linkedin_url}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve Humantic profile.")
        return None


def main():
    st.title("Chat with Assistants")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

    assistant_options = {
        "LinkedIn Persona Analyzer": "asst_IDB3oop3AS2Aoe5dZsjlvsak",
        "LinkedIn Post Generator": "asst_xMMUIRQFfQmZCI30ifkvkGHf",
        "Persona Mailer": "asst_7t7A2HYrr8UBDTVBTFiGJDGl"
    }

    assistant_name = st.selectbox("Choose an Assistant", list(assistant_options.keys()))
    assistant_id = assistant_options[assistant_name]

    csv_file = None
    if assistant_name == "Persona Mailer":
        csv_file = st.file_uploader("Upload a CSV file", type="csv")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What do you want to do?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        if not st.session_state.thread_id:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id
        else:
            thread = client.beta.threads.retrieve(st.session_state.thread_id)

        data = None
        if assistant_name == "Persona Mailer" and csv_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                tmp_file.write(csv_file.getbuffer())
                temp_file_path = tmp_file.name

            file = client.files.create(
                file=open(temp_file_path, "rb"),
                purpose='assistants'
            )
            data = [{"file_id": file.id, "tools": [{"type": "code_interpreter"}]}]


        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
            attachments=data if assistant_name == "Persona Mailer" and csv_file else None
        )

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            event_handler = StreamlitEventHandler(message_placeholder)

            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant_id,
                event_handler=event_handler,
            ) as stream:
                stream.until_done()

        st.session_state.messages.append({"role": "assistant", "content": event_handler.full_text})
        os.remove(temp_file_path)


if __name__ == "__main__":
    main()
