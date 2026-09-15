from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from backend.agents.state import AgentState
import sqlite3

from backend.agents.nodes.intent_classifier import classify_intent_node
from backend.agents.nodes.tool_nodes import (
    add_task_node, 
    list_tasks_node, 
    update_task_node, 
    delete_task_node, 
    summarize_tasks_node,
    follow_up_node
)
from backend.agents.nodes.response_node import generate_response_node

def route_intent(state: AgentState):
    """Conditional edge routing based on intent."""
    return state["intent"]

def build_graph():
    workflow = StateGraph(AgentState)
    
   
    workflow.add_node("intent_classifier", classify_intent_node)
    
    workflow.add_node("add_task", add_task_node)
    workflow.add_node("list_tasks", list_tasks_node)
    workflow.add_node("update_task", update_task_node)
    workflow.add_node("delete_task", delete_task_node)
    workflow.add_node("summarize_tasks", summarize_tasks_node)
    workflow.add_node("follow_up", follow_up_node)
    
    workflow.add_node("generate_response", generate_response_node)
    
    workflow.add_edge(START, "intent_classifier")
    
    workflow.add_conditional_edges(
        "intent_classifier",
        route_intent,
        {
            "add_task": "add_task",
            "list_tasks": "list_tasks",
            "update_task": "update_task",
            "delete_task": "delete_task",
            "summarize_tasks": "summarize_tasks",
            "follow_up": "follow_up"
        }
    )
    
    for tool_node in ["add_task", "list_tasks", "update_task", "delete_task", "summarize_tasks", "follow_up"]:
        workflow.add_edge(tool_node, "generate_response")
        
    workflow.add_edge("generate_response", END)
    
    conn = sqlite3.connect("tasks.db", check_same_thread=False)
    memory = SqliteSaver(conn)
    app = workflow.compile(checkpointer=memory)
    return app

agent_app = build_graph()
