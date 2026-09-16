from fastapi import APIRouter
from backend.schemas.api_schemas import ChatRequest, ChatResponse
from backend.agents.agent_graph import agent_app
from backend.services.task_service import TaskService
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger("productivityAssistant")
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Takes user input, passes it through the LangGraph AI workflow, 
    and returns the final conversational response.
    """
    config = {"configurable": {"thread_id": request.thread_id}}
    
    state_input = {
        "user_input": request.user_input,
        "messages": [HumanMessage(content=request.user_input)]
    }
    
    result = agent_app.invoke(state_input, config=config)
    
    return ChatResponse(response=result["response"])

@router.get("/tasks")
def get_tasks():
    """Returns all tasks directly from the database for the UI to display."""
    service = TaskService()
    tasks = service.get_all_tasks()
    return [{"id": t.id, "description": t.description, "status": t.status} for t in tasks]
