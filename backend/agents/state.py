from typing import TypedDict, Annotated, List, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
    user_input: str
    
    intent: str
    
    tool_result: str
    
    
    response: str
