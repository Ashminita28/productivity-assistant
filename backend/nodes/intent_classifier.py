from backend.agents.llm_factory import get_llm
from backend.states.agent_state import AgentState
from backend.prompts.intent_prompts import intent_prompt
from backend.schemas.agent_schemas import Intent
import logging

logger = logging.getLogger("productivityAssistant")

def classify_intent_node(state: AgentState) -> dict:
    """Classifies the user input into a specific intent."""
    logger.info("Node: classify_intent_node")
    llm = get_llm(structured_schema=Intent)
    
    chain = intent_prompt | llm
    
    try:
        messages = state.get("messages", state["user_input"])
        extracted = chain.invoke({"messages": messages})
        intent = extracted.intent
    except Exception as e:
        logger.error(f"Failed to classify intent: {e}")
        intent = "follow_up"
        
    valid_intents = ["add_task", "list_tasks", "update_task", "delete_task", "summarize_tasks", "follow_up"]
    if intent not in valid_intents:
        logger.warning(f"Invalid intent returned by LLM: {intent}. Defaulting to follow_up.")
        intent = "follow_up"
        
    logger.debug(f"Classified Intent: {intent}")
    return {"intent": intent}
