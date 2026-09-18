from typing import Dict, Any
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from backend.agents.llm_factory import get_llm
from backend.states.agent_state import AgentState
from backend.agents.tool_retriever import get_relevant_tools

def call_react_agent(state: AgentState) -> Dict[str, Any]:
    """Wrapper function to invoke the ReAct agent within our main graph."""
    system_text = "You are a helpful productivity assistant. You can manage tasks (add, update, delete) and query tasks (list, summarize) using your tools. Always be friendly and concise."
    
    summary = state.get("summary", "")
    if summary:
        system_text += f"\n\nHere is a summary of the earlier conversation for context:\n{summary}"
        
    system_prompt = SystemMessage(content=system_text)
    
    messages = [system_prompt] + list(state.get("messages", []))
    
   
    user_query = state.get("user_input", "")
    for msg in reversed(messages):
        if getattr(msg, "type", "") == "human" or type(msg).__name__ == "HumanMessage":
            user_query = getattr(msg, "content", user_query)
            break
            
    
    relevant_tools = get_relevant_tools(user_query, k=3)
    
    react_agent = create_agent(model=get_llm(), tools=relevant_tools, interrupt_before=["tools"])
    
    result = react_agent.invoke({"messages": messages})
    
   
    last_message = result["messages"][-1]
    response_text = last_message.content if hasattr(last_message, "content") else str(last_message)
    
    return {"messages": result["messages"], "response": response_text}
