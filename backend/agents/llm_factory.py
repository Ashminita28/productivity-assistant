"""Centralized LLM Factory for routing models across Gemini, Groq, and OpenRouter."""

from typing import Any
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from backend.config.env_config import settings

logger = logging.getLogger("productivityAssistant")

def get_llm(structured_schema=None, temperature: float = 0.1) -> Any:
    """Instantiate and return the LLM based on configured LLM_PROVIDER and LLM_MODEL.

    Supported Providers:
    1. openrouter
    2. groq
    3. cerebras
    4. gemini
    """
    provider = settings.LLM_PROVIDER.lower().strip()
    model_name = settings.LLM_MODEL.strip()

    llm = None

    
    if provider == "openrouter":
        logger.info(f"Initializing OpenRouter LLM: '{model_name}'")
        llm = ChatOpenAI(
            model=model_name,
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature,
        )

    
    elif provider == "groq":
        logger.info(f"Initializing Groq LLM: '{model_name}'")
        llm = ChatGroq(
            model=model_name,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=temperature,
            max_tokens=700,
        )

    
    elif provider == "cerebras":
        logger.info(f"Initializing Cerebras LLM: '{model_name}'")
        llm = ChatOpenAI(
            model=model_name,
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1",
            temperature=temperature,
            max_tokens=800,
        )

    
    else:
        logger.info(f"Initializing Gemini LLM: '{model_name}'")
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=temperature,
        )

    if structured_schema:
        return llm.with_structured_output(structured_schema)
    
    return llm

def extract_text_content(content: Any) -> str:
    """Extract clean string content whether it is a str or a list of content blocks."""
    if not content:
        return ""

    if isinstance(content, str):
        raw_text = content
    elif isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        raw_text = "\n".join(parts)
    else:
        raw_text = str(content)

    return raw_text.replace(r"\$", "$").replace("$", r"\$")
