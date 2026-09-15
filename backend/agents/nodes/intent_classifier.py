from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from backend.config.env_config import settings
from backend.agents.state import AgentState
from backend.agents.prompts import INTENT_SYSTEM_PROMPT
import logging

logger = logging.getLogger("productivityAssistant")

class IntentSchema(BaseModel):
    intent: str = Field(description="The exact category string: add_task, list_tasks, update_task, delete_task, summarize_tasks, or follow_up")

def classify_intent_node(state: AgentState) -> dict:
    """Classifies the user's intent to route to the correct tool."""
    logger.info("Node: classify_intent_node")
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", api_key=settings.LLM_API_KEY).with_structured_output(IntentSchema)
    
    messages = [
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        HumanMessage(content=state["user_input"])
    ]
    
    extracted = llm.invoke(messages)
    intent = extracted.intent.strip().lower()
    
    valid_intents = ["add_task", "list_tasks", "update_task", "delete_task", "summarize_tasks", "follow_up"]
    if intent not in valid_intents:
        logger.warning(f"Invalid intent returned by LLM: {intent}. Defaulting to follow_up.")
        intent = "follow_up"
        
    logger.debug(f"Classified Intent: {intent}")
    return {"intent": intent}
