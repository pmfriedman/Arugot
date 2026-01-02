"""LLM utilities for Ollama integration with LangSmith tracing support."""

import os
from langchain_ollama import OllamaLLM

from settings import settings

# Configure LangSmith environment variables
os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
if settings.langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project

# Default model configuration
DEFAULT_MODEL = "llama3.2:3b"
DEFAULT_BASE_URL = "http://localhost:11434"


async def query_ollama(prompt: str, model: str | None = None) -> str:
    """
    Query the Ollama model with a prompt and return the response.
    
    Args:
        prompt: The prompt to send to the model
        model: Optional model name override (defaults to llama3.2:3b)
        
    Returns:
        The model's response as a string
    """
    llm = OllamaLLM(
        model=model or DEFAULT_MODEL,
        base_url=DEFAULT_BASE_URL
    )
    
    response = await llm.ainvoke(prompt)
    return response

