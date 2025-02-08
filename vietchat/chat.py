import asyncio
from datetime import datetime, UTC
import os
from pathlib import Path
import streamlit as st
from vietchat import utils
from vietchat.ai_provider import AIProvider
from vietchat.audio import audio_utils
from vietchat.audio.base import Voice
from vietchat.settings import Settings
from vietchat.translation.translator import translate_text
from vietchat.storage import local as storage
from vietchat.utils import logger

st.set_page_config(page_title="Viet chat", layout="wide")

langs = ["vi", "en", "fr"]
depths = [1, 2, 3, 4]
default_prompt = """You are a vietnamese speaker making a conversation with a friend in vietnamese.
If you think there is an ambiguity with what your friend says, for exemple, if it doesn't fit the conversation, 
you may reword what it says with your words ands ask to confirm that you understand correctly.
If there is not ambiguity you will try to answer with no more than 2 sentences.
"""

if "settings" not in st.session_state:  
    st.session_state.settings = Settings()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_id" not in st.session_state:
    st.session_state.message_id = 0

if "voices" not in st.session_state:
    st.session_state.voices = ["gtts"]


def init_conversation_dir():
    st.session_state.conversation_dir = (
        f"{storage.root_conversation_dir}/conversation-{datetime.now(UTC).isoformat()}"
    )


if "conversation_dir" not in st.session_state:
    init_conversation_dir()

if "prompt" not in st.session_state:
    st.session_state.prompt = default_prompt


@st.dialog("Load conversation")
def load_conversation_dialog():
    conversations = storage.list_conversations()
    conversation = st.selectbox("Select conversation", conversations)
    if st.button("Load"):
        conversation_content, conversation_dir = storage.load_conversation(conversation)
        st.session_state.conversation_dir = conversation_dir
        st.session_state.messages = conversation_content["messages"]
        st.session_state.prompt = conversation_content["prompt"]
        st.session_state.select_voice = next(
            (
                voice
                for voice in st.session_state.voices
                if conversation_content.get("voice") == voice.id
            ),
            None,
        )
        st.session_state.select_lang = conversation_content.get("language")
        st.rerun()

def show_message(message):
    content = message["content"]
    st.markdown(content)

def show_message_additional_content(message, autoplay=False):
    fields = [field for field in ["audio", "translation", "think", "user_reformulation"] if field in message]
    if fields:
        tabs = st.tabs(fields)
        tab_fields = dict(zip(fields, tabs))
        if "user_reformulation" in message:
            with tab_fields["user_reformulation"]:
                st.markdown(message['user_reformulation'])
        if "think" in message:
            with tab_fields["think"]:
                if isinstance(message['think'], list):
                    for think in message['think']:
                        st.markdown(think)
                else:
                    st.markdown(message['think'])
        if "translation" in message:
            with tab_fields["translation"]:
                st.markdown(message['translation'])
        if "audio" in message:
            with tab_fields["audio"]:
                st.audio(f"{st.session_state.conversation_dir}/{message["audio"]}", autoplay=autoplay)


def get_message_prompt(prompt, settings: Settings):
    if settings.main_provider == "openai":
        return {
            "role": "developer",
            "content": [
                {
                    "type": "text",
                    "text": prompt + "You will also add one reformulation of the last user message.",
                }
            ],
        }
    else:
        return {
            "role": "system",
            "content": prompt,
        }


def answer(
    prompt, language, voice: Voice, depth, ai_provider: AIProvider, settings: Settings
):
    with st.chat_message("assistant"):
        context = [get_message_prompt(prompt, settings)] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[-depth:]
        ]
        logger.info("context %s", context)

        streaming = False
        response = ai_provider.text.get_completions_stream(context, stream=streaming)
        if settings.main_provider == "openai":
            logger.info("response %s", response)
            think = response["reasoning_steps"]
            user_reformulation = response["user_reformulation"]
            response = response["answer"]
        else:
            user_reformulation = None
            if streaming:
                think, response = utils.extract_think(st.write_stream(response))
            else:
                think, response = utils.extract_think(response)
        
        message = {
            "id": st.session_state.message_id,
            "role": "assistant",
            "content": response,
            "think": think,
            "user_reformulation": user_reformulation,
        }
        show_message(message)
        translation = asyncio.run(
            translate_text(
                response,
                source=language,
                target=settings.translation_target_lang,
            )
        )
        st.session_state.message_id += 1
        audio_file = f"audio-{st.session_state.message_id}-assistant.mp3"
        audio_file_path = f"{st.session_state.conversation_dir}/{audio_file}"
        ai_provider.tts[voice.provider].text_to_speech(
            response, audio_file_path, voice_id=voice.id, lang=language
        )
        message["translation"] = translation
        message["audio"]= audio_file
        show_message_additional_content(message, autoplay=True)
        st.session_state.messages.append(message)
        storage.dump_conversation(
            prompt,
            st.session_state.messages,
            voice.id,
            language,
            st.session_state.conversation_dir,
        )


def get_voice_order(voice: Voice):
    if voice.provider == "gtts":
        return ""
    else:
        return voice.provider + voice.name


def settings_panel():
    prompt_cont, options_cont, options_2_cont, action_cont = st.columns([4, 1, 1, 1])
    with prompt_cont:
        prompt = st.text_area("Prompt", value=st.session_state.prompt)
    with options_cont:
        lang = st.selectbox("Language", langs, key="select_lang")
        voice = st.selectbox(
            "Voice",
            options=sorted(st.session_state.voices, key=get_voice_order),
            key="select_voice",
            format_func=lambda voice: voice.provider + "-" + voice.name,
        )
    with options_2_cont:
        user_voice_context = st.selectbox(
            "user voice context", ["prompt", "first message", "last message"]
        )
        depth = st.selectbox("context depth", [1, 2, 3, 4], index=2)
    with action_cont:
        if st.button("New conversation"):
            st.session_state.message_id = 0
            st.session_state.messages = []
            init_conversation_dir()
            st.session_state.prompt = default_prompt
        if st.button("Load conversation"):
            load_conversation_dialog()
    return prompt, lang, voice, depth, user_voice_context


def get_api_key(settings: Settings):
    return settings.provider_settings[settings.main_provider].api_key


def main():
    settings = st.session_state.settings

    if "ai_provider" not in st.session_state:
        ai_provider = AIProvider(settings)
        st.session_state.ai_provider = ai_provider
        st.session_state.voices = ai_provider.tts_voices
    else:
        ai_provider: AIProvider = st.session_state.ai_provider

    prompt, lang, voice, depth, user_voice_context = settings_panel()

    with st.container(border=True):
        st.write("Conversation")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                show_message(message)
                show_message_additional_content(message)
        if (
            st.session_state.messages
            and st.session_state.messages[-1]["role"] == "user"
        ):
            answer(prompt, lang, voice, depth, ai_provider, settings)

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

            if not ai_provider:
                st.write("Please provide an API key to use the assistant")
            else:
                user_speech_text = ai_provider.speechtt.speech_to_text(
                    trimmed_audio_file_path, language=lang, prompt=hint
                )

                with st.form(key="user_message"):
                    user_message = st.text_input(
                        label="Your message", value=user_speech_text
                    )

                    if st.form_submit_button("submit"):
                        st.session_state.messages.append(
                            {
                                "id": st.session_state.message_id,
                                "role": "user",
                                "content": user_message,
                            }
                        )
                        st.rerun()


main()
