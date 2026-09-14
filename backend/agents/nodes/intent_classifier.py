from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.config.env_config import settings
from backend.agents.state import AgentState
from backend.agents.prompts import INTENT_SYSTEM_PROMPT
import logging

logger = logging.getLogger("productivityAssistant")

def classify_intent_node(state: AgentState) -> dict:
    """Classifies the user's intent to route to the correct tool."""
    logger.info("Node: classify_intent_node")
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=settings.LLM_API_KEY)
    
    messages = [
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=state["user_input"])
    ]
    
    response = llm.invoke(messages)
    intent = response.content.strip().lower()
    
    valid_intents = ["add_task", "list_tasks", "update_task", "delete_task", "summarize_tasks", "follow_up"]
    if intent not in valid_intents:
        logger.warning(f"Invalid intent returned by LLM: {intent}. Defaulting to follow_up.")
        intent = "follow_up"
        
    logger.debug(f"Classified Intent: {intent}")
    return {"intent": intent}
