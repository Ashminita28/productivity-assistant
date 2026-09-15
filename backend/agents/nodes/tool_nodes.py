from pydantic import BaseModel, Field
from backend.agents.state import AgentState
from backend.agents.llm_factory import get_llm
from backend.agents.tools import (
    execute_add_task, execute_list_tasks, 
    execute_update_task, execute_delete_task, 
    execute_summarize_tasks
)

class AddTaskSchema(BaseModel):
    description: str = Field(description="The description of the task to add.")

class UpdateTaskSchema(BaseModel):
    task_id: int = Field(description="The ID of the task to update.")
    status: str = Field(description="The new status of the task (e.g. Completed).")

class DeleteTaskSchema(BaseModel):
    task_id: int = Field(description="The ID of the task to delete.")

def add_task_node(state: AgentState) -> dict:
    llm = get_llm(structured_schema=AddTaskSchema)
    extracted = llm.invoke(state["user_input"])
    result = execute_add_task(extracted.description)
    return {"tool_result": result}

def list_tasks_node(state: AgentState) -> dict:
    result = execute_list_tasks()
    return {"tool_result": result}

def update_task_node(state: AgentState) -> dict:
    llm = get_llm(structured_schema=UpdateTaskSchema)
    extracted = llm.invoke(state["user_input"])
    result = execute_update_task(extracted.task_id, extracted.status)
    return {"tool_result": result}

def delete_task_node(state: AgentState) -> dict:
    llm = get_llm(structured_schema=DeleteTaskSchema)
    extracted = llm.invoke(state["user_input"])
    result = execute_delete_task(extracted.task_id)
    return {"tool_result": result}

def summarize_tasks_node(state: AgentState) -> dict:
    result = execute_summarize_tasks()
    return {"tool_result": result}
    
def follow_up_node(state: AgentState) -> dict:
    return {"tool_result": "I'm not exactly sure what you want to do. Could you please provide more details?"}
