from fastapi import FastAPI
from pydantic import BaseModel
from backend.agents.graph import agent_app
from backend.repositories.task_repo import TaskRepository
from backend.config.database_config import SessionLocal

app = FastAPI(title="Productivity Assistant API")

class ChatRequest(BaseModel):
    user_input: str
    thread_id: str = "default_thread"

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Takes user input, passes it through the LangGraph AI workflow, 
    and returns the final conversational response.
    """
   
    config = {"configurable": {"thread_id": request.thread_id}}
    
    
    state_input = {"user_input": request.user_input}
    
   
    result = agent_app.invoke(state_input, config=config)
    
    return ChatResponse(response=result["response"])

@app.get("/tasks")
def get_tasks():
    """Returns all tasks directly from the database for the UI to display."""
    db = SessionLocal()
    try:
        repo = TaskRepository(db)
        tasks = repo.get_all_tasks()
        return [{"id": t.id, "description": t.description, "status": t.status} for t in tasks]
    finally:
        db.close()
