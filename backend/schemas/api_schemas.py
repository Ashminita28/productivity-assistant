from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    user_input: str
    thread_id: str

class ChatResponse(BaseModel):
    response: str

class InterruptRequest(BaseModel):
    thread_id: str
    approved: bool
