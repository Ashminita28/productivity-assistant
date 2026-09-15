from backend.states.agent_state import AgentState
from backend.tools.task_tools import execute_summarize_tasks

def summarize_tasks_node(state: AgentState) -> dict:
    result = execute_summarize_tasks()
    return {"tool_result": result}
