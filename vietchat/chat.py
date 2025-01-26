from datetime import datetime, UTC
from io import BytesIO
import json
from openai import OpenAI
import streamlit as st
from vietchat.audio.speech_openai import speech_to_text, text_to_speech
from vietchat.translation.translator import translate
from pathlib import Path
import os

st.set_page_config(page_title="Viet chat", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

llm_model = "gpt-4o-mini"

root_conversation_dir = "data/conversations"


if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_id" not in st.session_state:
    st.session_state.message_id = 0

if "conversation_dir" not in st.session_state:
    st.session_state.conversation_dir = (
        f"{root_conversation_dir}/conversation-{datetime.now(UTC).isoformat()}"
    )

if "prompt" not in st.session_state:
    st.session_state.prompt = """You are a vietnamese speaker making a conversation with a friend in vietnamese.
You will try to answer with no more than 2 sentences."""


@st.dialog("Load conversation")
def load_conversation_dialog():
    conversations = [
        name
        for name in os.listdir(root_conversation_dir)
        if os.path.isdir(os.path.join(root_conversation_dir, name))
    ]
    conversation = st.selectbox("Select conversation", conversations)
    if st.button("Load"):
        st.session_state.conversation_dir = f"{root_conversation_dir}/{conversation}"
        with open(f"{st.session_state.conversation_dir}/conversation.json", "r") as f:
            conversation_content = json.load(f)
            st.session_state.messages = conversation_content["messages"]
            st.session_state.prompt = conversation_content["prompt"]
        st.rerun()


def dump_conversation():
    with open(f"{st.session_state.conversation_dir}/conversation.json", "w", encoding='utf8') as f:
        conversation_content = {
          "prompt" : st.session_state.prompt,
          "messages": st.session_state.messages
        }
        json.dump(conversation_content, f, ensure_ascii=False, indent=2)


def save_bytes(data: BytesIO, file_path: str):
    with open(file_path, "wb") as file:
        file.write(data.getbuffer())


def show_options(message):
    if "translation" in message:
        st.markdown(f"Translation: {message['translation']}")
    if "audio" in message:
        st.audio(message["audio"])


def get_message_prompt(prompt):
    return {
        "role": "developer",
        "content": [
            {
                "type": "text",
                "text": prompt,
            }
        ],
    }


def answer(prompt, language):
    with st.chat_message("assistant"):
        context = [get_message_prompt(prompt)] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-2:]
        ]
        print(context)
        stream = client.chat.completions.create(
            model=llm_model,
            messages=context,
            stream=True,
        )
        response = st.write_stream(stream)
        # translation = translate(response, source_language=language, target="fr")
        st.session_state.message_id += 1
        audio_file = f"{st.session_state.conversation_dir}/audio-{st.session_state.message_id}-assistant.wav"
        text_to_speech(response, client, audio_file)
        message = {
            "id": st.session_state.message_id,
            "role": "assistant",
            "content": response,
            # "translation": translation,
            "audio": audio_file,
        }
        show_options(message)
        st.session_state.messages.append(message)
        dump_conversation()


def main():
    prompt_cont, options_cont = st.columns([5, 1])
    with prompt_cont:
        prompt = st.text_area("Prompt", value=st.session_state.prompt)
    with options_cont:
        lang = st.selectbox("Language", ["vi", "en"])
        if st.button("Load conversation"):
            load_conversation_dialog()

    with st.container(border=True):
        st.write("Conversation")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                show_options(message)
        if (
            st.session_state.messages
            and st.session_state.messages[-1]["role"] == "user"
        ):
            answer(prompt, lang)

    with st.container(border=True):
        audio_value = st.audio_input("Record a voice message")

        if audio_value:
            st.session_state.message_id += 1
            Path(st.session_state.conversation_dir).mkdir(parents=True, exist_ok=True)
            audio_file = f"{st.session_state.conversation_dir}/audio-{st.session_state.message_id}-user.wav"
            save_bytes(audio_value, audio_file)
            user_speech_text = speech_to_text(audio_file, client, language=lang)

            with st.chat_message("user"):
                st.markdown(user_speech_text)

            if st.button("submit"):
                st.session_state.messages.append(
                    {
                        "id": st.session_state.message_id,
                        "role": "user",
                        "content": user_speech_text,
                    }
                )
                st.rerun()


main()
