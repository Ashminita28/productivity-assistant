from backend.states.agent_state import AgentState
from backend.agents.llm_factory import get_llm
from backend.tools.task_tools import execute_update_task
from backend.schemas.agent_schemas import UpdateTask

def update_task_node(state: AgentState) -> dict:
    llm = get_llm(structured_schema=UpdateTask)
    messages = state.get("messages", state["user_input"])
    extracted = llm.invoke(messages)
    result = execute_update_task(extracted.task_id, extracted.status, getattr(extracted, "description", None))
    return {"tool_result": result}
