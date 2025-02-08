import json


def test_get_completions_stream(openai_text):
    response = openai_text.get_completions_stream(
        messages=[
            {"role": "developer", "content": [{"type": "text", "text": 
"""you're a chatbot assistant that helps users with their questions. 
You will also add one reformulation of the last user message.
"""}]},
            {"role": "user", "content": [{"type": "text", "text": "Hello how are you?"}]},
        ],
        stream=False,
    )
    print(json.dumps(response, indent=2))
