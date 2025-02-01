import asyncio
from datetime import datetime, UTC
import os
from openai import OpenAI
import streamlit as st
from vietchat.audio import audio_utils, speech_basic
from vietchat.audio.speech_openai import speech_to_text, text_to_speech
from vietchat.settings import Settings
from vietchat.translation.translator import translate_text
from pathlib import Path
from storage import local as storage

st.set_page_config(page_title="Viet chat", layout="wide")

langs = ["vi", "en", "fr"]
voices = [
    "gtts",
    "alloy",
    "ash",
    "coral",
    "echo",
    "fable",
    "onyx",
    "nova",
    "sage",
    "shimmer",
]
depths = [1, 2, 3, 4]

if "settings" not in st.session_state:
    st.session_state.settings = Settings()

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
        st.session_state.voice = conversation_content.get("voice")
        st.session_state.select_voice = conversation_content.get("voice")
        st.session_state.select_lang = conversation_content.get("language")
        st.rerun()


def show_message_additional_content(message):
    if "translation" in message:
        with st.expander("translation"):
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


def answer(prompt, language, voice, depth, client, settings):
    with st.chat_message("assistant"):
        context = [get_message_prompt(prompt)] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-depth:]
        ]
        print(context)
        stream = client.chat.completions.create(
            model=settings.llm_model,
            messages=context,
            stream=True,
        )
        response = st.write_stream(stream)
        translation = asyncio.run(
            translate_text(
                response,
                source=language,
                target=settings.translation_target_lang,
            )
        )
        st.session_state.message_id += 1
        audio_file = f"audio-{st.session_state.message_id}-assistant.wav"
        audio_file_path = f"{st.session_state.conversation_dir}/{audio_file}"
        if voice == "gtts":
            speech_basic.text_to_speech(response, audio_file_path, lang=language)
        else:
            text_to_speech(response, client, audio_file_path, voice=voice)
        message = {
            "id": st.session_state.message_id,
            "role": "assistant",
            "content": response,
            "translation": translation,
            "audio": audio_file,
        }
        show_message_additional_content(message)
        st.session_state.messages.append(message)
        storage.dump_conversation(
            prompt,
            st.session_state.messages,
            voice,
            language,
            st.session_state.conversation_dir,
        )


def settings_panel():
    prompt_cont, options_cont, options_2_cont, action_cont = st.columns([4, 1, 1, 1])
    with prompt_cont:
        prompt = st.text_area("Prompt", value=st.session_state.prompt)
    with options_cont:
        lang = st.selectbox("Language", langs, key="select_lang")
        voice = st.selectbox("Voice", voices, key="select_voice")
    with options_2_cont:
        user_voice_context = st.selectbox(
            "user voice context", ["prompt", "first message", "last message"]
        )
        depth = st.selectbox("context depth", [1, 2, 3, 4], index=1)
    with action_cont:
        if st.button("Load conversation"):
            load_conversation_dialog()
        api_key = st.text_input("API key")
    return prompt, lang, voice, depth, user_voice_context, api_key


def main():
    settings = st.session_state.settings
    prompt, lang, voice, depth, user_voice_context, api_key = settings_panel()
    if (settings.openai_api_key or api_key) and "client" not in st.session_state:
        st.session_state.client = OpenAI(api_key=settings.openai_api_key or api_key)
    with st.container(border=True):
        st.write("Conversation")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                show_message_additional_content(message)
        if (
            st.session_state.messages
            and st.session_state.messages[-1]["role"] == "user"
        ):
            answer(prompt, lang, voice, depth, st.session_state.client, settings)

    with st.container(border=True):
        audio_value = st.audio_input("Record a voice message")

        if audio_value:
            st.session_state.message_id += 1
            Path(st.session_state.conversation_dir).mkdir(parents=True, exist_ok=True)
            audio_file = f"audio-{st.session_state.message_id}-user.wav"
            audio_file_path = f"{st.session_state.conversation_dir}/{audio_file}"
            storage.save_bytes(audio_value, audio_file_path)
            _, trimmed_audio_file_path = audio_utils.trim_start(audio_file_path)
            os.remove(audio_file_path)
            
            hint = prompt
            if st.session_state.messages:
                if user_voice_context == "first message":
                    hint = st.session_state.messages[1]["content"]
                if user_voice_context == "last message":
                    hint = st.session_state.messages[-1]["content"]

            if "client" not in st.session_state:
                st.write("Please provide an API key to use the assistant")
            else:
                user_speech_text = speech_to_text(
                    trimmed_audio_file_path, st.session_state.client, language=lang, prompt=hint
                )

                user_message = st.text_input(label="Your message", value=user_speech_text)

                if st.button("submit"):
                    st.session_state.messages.append(
                        {
                            "id": st.session_state.message_id,
                            "role": "user",
                            "content": user_message,
                        }
                    )
                    st.rerun()


main()
