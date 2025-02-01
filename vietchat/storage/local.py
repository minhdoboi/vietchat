from io import BytesIO
import os
import json

root_conversation_dir = "data/conversations"


def dump_conversation(prompt, messages, voice, language, conversation_dir):
    with open(f"{conversation_dir}/conversation.json", "w", encoding="utf8") as f:
        conversation_content = {
            "prompt": prompt,
            "messages": messages,
            "voice": voice,
            "language": language,
        }
        json.dump(conversation_content, f, ensure_ascii=False, indent=2)


def list_conversations():
    return [
        name
        for name in os.listdir(root_conversation_dir)
        if os.path.isdir(os.path.join(root_conversation_dir, name))
    ]


def load_conversation(conversation):
    conversation_dir = f"{root_conversation_dir}/{conversation}"
    with open(f"{conversation_dir}/conversation.json", "r") as f:
        conversation_content = json.load(f)
    return conversation_content, conversation_dir


def save_bytes(data: BytesIO, file_path: str):
    with open(file_path, "wb") as file:
        file.write(data.getbuffer())
