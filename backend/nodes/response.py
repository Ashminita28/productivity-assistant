from langchain_core.messages import AIMessage
from backend.agents.llm_factory import get_llm, extract_text_content
from backend.states.agent_state import AgentState
from backend.prompts.response_prompts import response_prompt

def generate_response_node(state: AgentState) -> dict:
    """Takes the tool result and generates a friendly response."""
    if state.get("is_safe") is False:
        msg = state.get("tool_result", "Your request was blocked by safety policies.")
        return {
            "response": msg,
            "messages": [AIMessage(content=msg)]
        }
        
    llm = get_llm()
    
    chain = response_prompt | llm
    
    try:
        result = chain.invoke({
            "user_input": state["user_input"],
            "tool_result": state.get("tool_result", "No tool result provided.")
        })
        content = extract_text_content(getattr(result, "content", str(result)))
    except Exception as e:
        print(f"Error generating response: {e}")
        content = "An error occurred while generating the response."
        
    return {
        "response": content,
        "messages": [AIMessage(content=content)]
    }
