from backend.states.agent_state import AgentState

def follow_up_node(state: AgentState) -> dict:
    return {"tool_result": "I'm not exactly sure what you want to do. Could you please provide more details?"}
