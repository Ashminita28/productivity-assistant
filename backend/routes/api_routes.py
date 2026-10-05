from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from backend.schemas.api_schemas import ChatRequest, ChatResponse, InterruptRequest
from backend.services.task_service import TaskService
from backend.services.chat_service import ChatService
from backend.services.rag_service import rag_service
from langchain_core.messages import HumanMessage
import logging
import os
import shutil

logger = logging.getLogger("productivityAssistant")
router = APIRouter()
chat_service = ChatService()

@router.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@router.get("/documents")
def list_documents():
    """Returns a list of all ingested documents."""
    upload_dir = os.path.join(os.getcwd(), "data", "uploads")
    if not os.path.exists(upload_dir):
        return {"documents": []}
    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    return {"documents": files}

@router.delete("/documents/{filename}")
def delete_document(filename: str):
    """Deletes a document from the file system and the vector DB."""
    upload_dir = os.path.join(os.getcwd(), "data", "uploads")
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": f"{filename} deleted successfully."}
    raise HTTPException(status_code=404, detail="File not found")

@router.post("/documents/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Accepts a file upload, saves it, and ingests it into Qdrant."""
    if not file.filename.lower().endswith(('.pdf', '.txt', '.docx', '.md')):
        raise HTTPException(status_code=400, detail="Unsupported file format.")
        
    upload_dir = os.path.join(os.getcwd(), "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"File uploaded successfully to {file_path}. Starting ingestion...")
        
        ingest_result = rag_service.ingest_document(file_path)
        logger.info(ingest_result)
        
        return {"filename": file.filename, "file_path": file_path, "message": "File successfully ingested into vector database.", "details": ingest_result}
    except Exception as e:
        logger.error(f"Error saving/ingesting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not process file: {str(e)}")



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
