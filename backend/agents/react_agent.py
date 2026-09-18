from typing import Dict, Any
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from backend.agents.llm_factory import get_llm
from backend.states.agent_state import AgentState
from backend.tools.task_tools import (
    AddTaskTool, ListTasksTool, UpdateTaskTool, 
    DeleteTaskTool, SummarizeTasksTool
)

def get_react_agent():
    """Initializes and returns the Single Tool Calling ReAct agent."""
    tools = [
        AddTaskTool(), ListTasksTool(), UpdateTaskTool(), 
        DeleteTaskTool(), SummarizeTasksTool()
    ]
    
    return create_agent(model=get_llm(), tools=tools, interrupt_before=["tools"])


react_agent = get_react_agent()

def call_react_agent(state: AgentState) -> Dict[str, Any]:
    """Wrapper function to invoke the ReAct agent within our main graph."""
    system_text = "You are a helpful productivity assistant. You can manage tasks (add, update, delete) and query tasks (list, summarize) using your tools. Always be friendly and concise."
    
    summary = state.get("summary", "")
    if summary:
        system_text += f"\n\nHere is a summary of the earlier conversation for context:\n{summary}"
        
    system_prompt = SystemMessage(content=system_text)
    
    messages = [system_prompt] + list(state.get("messages", []))
    result = react_agent.invoke({"messages": messages})
    
   
    last_message = result["messages"][-1]
    response_text = last_message.content if hasattr(last_message, "content") else str(last_message)
    
    return {"messages": result["messages"], "response": response_text}
