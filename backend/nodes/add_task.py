from backend.states.agent_state import AgentState
from backend.agents.llm_factory import get_llm
from backend.tools.task_tools import execute_add_task
from backend.schemas.agent_schemas import AddTask

def add_task_node(state: AgentState) -> dict:
    llm = get_llm(structured_schema=AddTask)
    messages = state.get("messages", state["user_input"])
    extracted = llm.invoke(messages)
    result = execute_add_task(extracted.description)
    return {"tool_result": result}
