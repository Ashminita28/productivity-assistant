from backend.states.agent_state import AgentState
from backend.agents.llm_factory import get_llm
from backend.tools.task_tools import execute_delete_task
from backend.schemas.agent_schemas import DeleteTask

def delete_task_node(state: AgentState) -> dict:
    llm = get_llm(structured_schema=DeleteTask)
    messages = state.get("messages", state["user_input"])
    extracted = llm.invoke(messages)
    result = execute_delete_task(extracted.task_id)
    return {"tool_result": result}
