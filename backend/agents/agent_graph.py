from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from backend.states.agent_state import AgentState
import sqlite3
from backend.guardrails.guardrails import check_input_guardrail_node, check_output_guardrail_node
from backend.agents.react_agent import call_react_agent
from langchain_core.messages import AIMessage

def handle_unsafe_input(state: AgentState):
    """Generates a response if the input guardrail fails."""
    msg = state.get("tool_result", "Your request was blocked by safety policies.")
    return {
        "response": msg,
        "messages": [AIMessage(content=msg)]
    }

def route_guardrail(state: AgentState):
    """Conditional edge routing based on safety."""
    if state.get("is_safe", True):
        return "react_agent"
    return "unsafe_handler"

def build_graph():
    workflow = StateGraph(AgentState)
    
   
    workflow.add_node("input_guardrail", check_input_guardrail_node)
    
   
    workflow.add_node("react_agent", call_react_agent)
    
   
    workflow.add_node("unsafe_handler", handle_unsafe_input)
    
   
    workflow.add_node("output_guardrail", check_output_guardrail_node)
    
   
    workflow.add_edge(START, "input_guardrail")
    
    workflow.add_conditional_edges(
        "input_guardrail",
        route_guardrail,
        {
            "react_agent": "react_agent",
            "unsafe_handler": "unsafe_handler"
        }
    )
    
    workflow.add_edge("react_agent", "output_guardrail")
    workflow.add_edge("unsafe_handler", "output_guardrail")
    workflow.add_edge("output_guardrail", END)
    
    
    conn = sqlite3.connect("tasks.db", check_same_thread=False)
    memory = SqliteSaver(conn)
    app = workflow.compile(checkpointer=memory)
    return app

agent_app = build_graph()
