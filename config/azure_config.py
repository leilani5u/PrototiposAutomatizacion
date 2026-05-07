from openai import AzureOpenAI
from config.settings import (
    API_VERSION_CHAT,
    API_VERSION_TRANSCRIBE,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_KEY,
)

chat_client = AzureOpenAI(
    api_version=API_VERSION_CHAT,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
)

transcribe_client = AzureOpenAI(
    api_version=API_VERSION_TRANSCRIBE,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
)
