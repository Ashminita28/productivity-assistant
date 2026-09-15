from langchain_core.messages import HumanMessage, AIMessage
from backend.agents.llm_factory import get_llm
from backend.agents.state import AgentState
from backend.agents.prompts import RESPONSE_SYSTEM_PROMPT

def generate_response_node(state: AgentState) -> dict:
    """Takes the tool result and generates a friendly response."""
    llm = get_llm()
    
    prompt = RESPONSE_SYSTEM_PROMPT.format(
        user_input=state["user_input"],
        tool_result=state["tool_result"]
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    content = response.content
    if isinstance(content, list):
        content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
    
    return {
        "response": content,
        "messages": [AIMessage(content=content)]
    }
