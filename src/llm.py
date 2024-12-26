import os

from langchain_groq.chat_models import ChatGroq
from langchain_ollama import ChatOllama

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


if os.getenv("USE_GROQ") == "no":
    llm = ChatOllama(model=os.getenv("OLLAMA_CHAT_MODEL"), temperature=0.0)
else:
    llm = ChatGroq(
        model=os.getenv("CHAT_GROQ_MODEL"),
        stop_sequences="[end]",
        temperature=0.0,
    )
