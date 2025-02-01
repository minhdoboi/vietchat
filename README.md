# Stupid bot for speaking vietnamese

A bot using OpenAI or Groq to speak vietnamese

## Usage

* write a situation in the prompt
* discuss a bit with the bot
* go speak with real vietnamese people
* fail

## Install

```
poetry install
```

copy `example.secrets.toml` to `.streamlit/secrets.toml` and fill the config.
copy `example.env` to `.env` and fill the config.


## Run

```
poetry run python -m streamlit run vietchat/chat.py 
```
