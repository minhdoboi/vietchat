from datetime import datetime, UTC
from io import BytesIO
import json
from openai import OpenAI
import streamlit as st
from vietchat.audio.speech_openai import speech_to_text, text_to_speech
from vietchat.translation.translator import translate
from pathlib import Path
from storage import local as storage
import os

st.set_page_config(page_title="Viet chat", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

llm_model = "gpt-4o-mini"


if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_id" not in st.session_state:
    st.session_state.message_id = 0

if "conversation_dir" not in st.session_state:
    st.session_state.conversation_dir = (
        f"{storage.root_conversation_dir}/conversation-{datetime.now(UTC).isoformat()}"
    )

if "prompt" not in st.session_state:
    st.session_state.prompt = """You are a vietnamese speaker making a conversation with a friend in vietnamese.
You will try to answer with no more than 2 sentences."""


@st.dialog("Load conversation")
def load_conversation_dialog():
    conversations = storage.list_conversations()
    conversation = st.selectbox("Select conversation", conversations)
    if st.button("Load"):
        conversation_content, conversation_dir = storage.load_conversation(conversation)
        st.session_state.conversation_dir = conversation_dir
        st.session_state.messages = conversation_content["messages"]
        st.session_state.prompt = conversation_content["prompt"]
        st.rerun()


def show_options(message):
    if "translation" in message:
        st.markdown(f"Translation: {message['translation']}")
    if "audio" in message:
        st.audio(f"{st.session_state.conversation_dir}/{message["audio"]}")


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
        audio_file = f"audio-{st.session_state.message_id}-assistant.wav"
        audio_file_path = f"{st.session_state.conversation_dir}/{audio_file}"
        text_to_speech(response, client, audio_file_path)
        message = {
            "id": st.session_state.message_id,
            "role": "assistant",
            "content": response,
            # "translation": translation,
            "audio": audio_file,
        }
        show_options(message)
        st.session_state.messages.append(message)
        storage.dump_conversation(prompt, st.session_state.messages, st.session_state.conversation_dir)


def settings_panel():
    prompt_cont, options_cont = st.columns([5, 1])
    with prompt_cont:
        prompt = st.text_area("Prompt", value=st.session_state.prompt)
    with options_cont:
        lang = st.selectbox("Language", ["vi", "en", "fr"])
        if st.button("Load conversation"):
            load_conversation_dialog()
    return prompt, lang

def main():
    prompt, lang = settings_panel()
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
            audio_file = f"audio-{st.session_state.message_id}-user.wav"
            audio_file_path = f"{st.session_state.conversation_dir}/{audio_file}"
            storage.save_bytes(audio_value, audio_file_path)
            user_speech_text = speech_to_text(audio_file_path, client, language=lang, prompt=prompt)

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
