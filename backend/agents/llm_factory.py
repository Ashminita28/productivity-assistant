"""Centralized LLM Factory for routing models across Gemini, Groq, and OpenRouter."""

from typing import Any
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.config.env_config import settings

logger = logging.getLogger("productivityAssistant")

def get_embeddings():
    return OllamaEmbeddings(
        model="bge-m3",
        base_url=settings.OLLAMA_BASE_URL
    )

def _init_provider(provider: str, model_name: str, temperature: float, max_tokens: int) -> Any:
    """Helper to initialize a specific LLM provider."""
    provider = provider.lower().strip()
    if provider == "ollama":
        return ChatOllama(
            model=model_name,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=temperature,
            num_predict=max_tokens,
        )
    elif provider == "openrouter":
        return ChatOpenAI(
            model=model_name,
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
        )
    elif provider == "groq":
        return ChatGroq(
            model=model_name,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
        )
    elif provider == "cerebras":
        return ChatOpenAI(
            model=model_name,
            api_key=settings.CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1",
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=True,
        )
    else:
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=temperature,
            max_output_tokens=max_tokens,
            streaming=True,
        )

def get_llm(structured_schema=None, temperature: float = 0.1, task_type: str = "smart", max_tokens: int = 1000) -> Any:
    """Instantiate and return the LLM based on task type, with automatic fallbacks."""
    if task_type == "fast":
        primary_provider = settings.FAST_LLM_PROVIDER.lower().strip()
        primary_model = settings.FAST_LLM_MODEL.strip()
    else:
        primary_provider = settings.SMART_LLM_PROVIDER.lower().strip()
        primary_model = settings.SMART_LLM_MODEL.strip()

    
    logger.info(f"Initializing Primary LLM ({primary_provider}): '{primary_model}'")
    primary_llm = _init_provider(primary_provider, primary_model, temperature, max_tokens)

   
    backup_configs = [
        ("gemini", "gemini-2.5-flash"),
        ("groq", "llama3-8b-8192"),
        ("openrouter", "google/gemini-2.5-flash")
    ]

    backup_llms = []
    for bp, bm in backup_configs:
        if bp != primary_provider: 
            try:
                backup_llms.append(_init_provider(bp, bm, temperature, max_tokens))
            except Exception as e:
                logger.warning(f"Could not initialize backup {bp}: {e}")

    
    if structured_schema:
        primary_llm = primary_llm.with_structured_output(structured_schema)
        backup_llms = [llm.with_structured_output(structured_schema) for llm in backup_llms]

    if backup_llms:
        logger.info(f"Binding {len(backup_llms)} fallbacks to primary LLM.")
        return primary_llm.with_fallbacks(backup_llms)
        
    return primary_llm

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
