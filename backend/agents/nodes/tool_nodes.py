from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from backend.config.env_config import settings
from backend.agents.state import AgentState
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

def _get_llm():
    return ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=settings.LLM_API_KEY)

def add_task_node(state: AgentState) -> dict:
    llm = _get_llm().with_structured_output(AddTaskSchema)
    extracted = llm.invoke(state["user_input"])
    result = execute_add_task(extracted.description)
    return {"tool_result": result}

def list_tasks_node(state: AgentState) -> dict:
    result = execute_list_tasks()
    return {"tool_result": result}

def update_task_node(state: AgentState) -> dict:
    llm = _get_llm().with_structured_output(UpdateTaskSchema)
    extracted = llm.invoke(state["user_input"])
    result = execute_update_task(extracted.task_id, extracted.status)
    return {"tool_result": result}

def delete_task_node(state: AgentState) -> dict:
    llm = _get_llm().with_structured_output(DeleteTaskSchema)
    extracted = llm.invoke(state["user_input"])
    result = execute_delete_task(extracted.task_id)
    return {"tool_result": result}

def summarize_tasks_node(state: AgentState) -> dict:
    result = execute_summarize_tasks()
    return {"tool_result": result}
    
def follow_up_node(state: AgentState) -> dict:
    return {"tool_result": "I'm not exactly sure what you want to do. Could you please provide more details?"}
