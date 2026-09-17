from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from backend.agents.llm_factory import get_llm
from backend.states.agent_state import AgentState
from backend.schemas.agent_schemas import Guardrail
from backend.prompts.guardrail_prompts import input_guardrail_prompt, output_guardrail_prompt
import logging

logger = logging.getLogger("productivityAssistant")

def check_input_guardrail_node(state: AgentState) -> dict:
    """Checks the user input against safety guidelines."""
    logger.info("Node: check_input_guardrail_node")
    
    llm = get_llm(structured_schema=Guardrail, task_type="fast")
    
    chain = input_guardrail_prompt | llm
    
    try:
        extracted = chain.invoke({"user_input": state["user_input"]})
        is_safe = extracted.is_safe
        reason = extracted.reason
    except Exception as e:
        logger.error(f"Guardrail check failed: {e}")
        error_details = str(e)
        msg = f"System Error: The AI provider encountered an issue: {error_details}"
        return {
            "is_safe": False,
            "tool_result": msg
        }
        
    logger.debug(f"Guardrail Result - Safe: {is_safe}, Reason: {reason}")
    
    if not is_safe:
        return {
            "is_safe": False,
            "tool_result": f"Security Alert: Your request was blocked because it violated safety policies. Reason: {reason}"
        }
    
    return {"is_safe": True}

def check_output_guardrail_node(state: AgentState) -> dict:
    """Checks the generated LLM response against safety guidelines."""
    logger.info("Node: check_output_guardrail_node")
    
    if not state.get("is_safe", True):
        return {}
        
    llm = get_llm(structured_schema=Guardrail, task_type="fast")
    
    chain = output_guardrail_prompt | llm
    
    try:
        extracted = chain.invoke({"response": state.get("response", "")})
        is_safe = extracted.is_safe
        reason = extracted.reason
    except Exception as e:
        logger.error(f"Output Guardrail check failed: {e}")
        error_details = str(e)
        msg = f"System Error: The AI provider encountered an issue: {error_details}"
        return {
            "response": msg,
            "messages": [AIMessage(content=msg)]
        }
        
    logger.debug(f"Output Guardrail Result - Safe: {is_safe}, Reason: {reason}")
    
    if not is_safe:
        logger.warning(f"Output blocked: {reason}")
        return {
            "response": "I apologize, but I cannot provide that response due to safety policies.",
            "messages": [AIMessage(content="I apologize, but I cannot provide that response due to safety policies.")]
        }
    
    return {}
