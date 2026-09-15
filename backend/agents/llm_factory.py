from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config.env_config import settings

def get_llm(structured_schema=None):
    """
    Returns an instance of the configured LLM.
    If structured_schema is provided, attaches the schema using with_structured_output.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", api_key=settings.LLM_API_KEY)
    
    if structured_schema:
        return llm.with_structured_output(structured_schema)
    
    return llm
