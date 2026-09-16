from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_input: str
    thread_id: str = "default_thread"

class ChatResponse(BaseModel):
    response: str
