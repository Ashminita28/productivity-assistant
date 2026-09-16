from backend.states.agent_state import AgentState
from backend.tools.task_tools import execute_list_tasks

def list_tasks_node(state: AgentState) -> dict:
    result = execute_list_tasks()
    return {"tool_result": result}
