from backend.states.agent_state import AgentState
from backend.config.env_config import settings
from langchain_core.messages import AIMessage
import logging
import requests

logger = logging.getLogger("productivityAssistant")

def check_input_guardrail_node(state: AgentState) -> dict:
    """Checks the user input against safety guidelines via NeMo Docker service."""
    logger.info("Node: check_input_guardrail_node (NeMo via HTTP)")
    messages = [{"role": "user", "content": state["user_input"]}]
    
    try:
        res = requests.post(
            f"{settings.NEMO_URL}/v1/chat/completions",
            json={"messages": messages},
            timeout=10
        )
        res.raise_for_status()
        
        data = res.json()
        response_text = data["choices"][0]["message"]["content"]
        
        if "sorry" in response_text.lower() and "cannot assist" in response_text.lower():
            is_safe = False
            reason = response_text
        else:
            is_safe = True
            reason = "NeMo: Input Passed"
            
    except Exception as e:
        logger.error(f"NeMo HTTP Input check failed: {e}")
        return {"is_safe": False, "tool_result": f"System Error: NeMo Service Unreachable"}
        
    logger.debug(f"NeMo Input Guardrail Result - Safe: {is_safe}, Reason: {reason}")
    
    if not is_safe:
        return {
            "is_safe": False,
            "tool_result": f"Security Alert: Your request was blocked by NeMo Guardrails."
        }
    
    return {"is_safe": True}

def check_output_guardrail_node(state: AgentState) -> dict:
    """Checks the generated LLM response against safety guidelines via NeMo Docker service."""
    logger.info("Node: check_output_guardrail_node (NeMo via HTTP)")
    if not state.get("is_safe", True):
        return {}
        
    messages = [{"role": "assistant", "content": state.get("response", "")}]
    
    try:
        res = requests.post(
            f"{settings.NEMO_URL}/v1/chat/completions",
            json={"messages": messages},
            timeout=10
        )
        res.raise_for_status()
        
        data = res.json()
        response_text = data["choices"][0]["message"]["content"]
        
        if "sorry" in response_text.lower() and "cannot assist" in response_text.lower():
            is_safe = False
            reason = "NeMo: Output Blocked"
        else:
            is_safe = True
            reason = "NeMo: Output Passed"
            
    except Exception as e:
        logger.error(f"NeMo HTTP Output check failed: {e}")
        msg = f"System Error: NeMo Service Unreachable"
        return {
            "response": msg,
            "messages": [AIMessage(content=msg)]
        }
        
    if not is_safe:
        logger.warning(f"Output blocked: {reason}")
        return {
            "response": "I apologize, but I cannot provide that response due to safety policies.",
            "messages": [AIMessage(content="I apologize, but I cannot provide that response due to safety policies.")]
        }
    
    return {}
