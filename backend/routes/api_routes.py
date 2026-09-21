from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.schemas.api_schemas import ChatRequest, ChatResponse, InterruptRequest
from backend.services.task_service import TaskService
from backend.services.chat_service import ChatService
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger("productivityAssistant")
router = APIRouter()
chat_service = ChatService()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Takes user input, passes it through the LangGraph AI workflow, 
    and returns the final conversational response synchronously.
    """
    config = {"configurable": {"thread_id": request.thread_id}}
    
    state_input = {
        "user_input": request.user_input,
        "messages": [HumanMessage(content=request.user_input)]
    }
    
    response = chat_service.chat_sync(state_input, config)
    
    return ChatResponse(response=response)

@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Streams the response tokens natively from the LangGraph agent."""
    config = {"configurable": {"thread_id": request.thread_id}}
    
    state_input = {
        "user_input": request.user_input,
        "messages": [HumanMessage(content=request.user_input)]
    }
    
    return StreamingResponse(chat_service.stream_chat(state_input, config), media_type="text/plain")

@router.post("/chat/respond_interrupt")
async def chat_respond_interrupt_endpoint(request: InterruptRequest):
    """Resumes the graph after a human approval or rejection."""
    config = {"configurable": {"thread_id": request.thread_id}}
    return StreamingResponse(chat_service.respond_interrupt(request.approved, config), media_type="text/plain")

@router.get("/chat/history/{thread_id}")
def get_chat_history(thread_id: str):
    """Retrieves chat history from LangGraph's SQLite memory."""
    history = chat_service.get_chat_history(thread_id)
    return {"messages": history}

@router.get("/tasks")
def get_tasks():
    """Returns all tasks directly from the database for the UI to display."""
    service = TaskService()
    tasks = service.get_all_tasks()
    return [{"id": t.id, "description": t.description, "status": t.status} for t in tasks]
