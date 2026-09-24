from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from backend.states.agent_state import AgentState
import sqlite3
from backend.guardrails.guardrails import check_input_guardrail_node, check_output_guardrail_node
from backend.nodes.history_manager import summarize_history_node
from langchain_core.messages import AIMessage
from backend.config.env_config import settings
from backend.agents.react_agent import react_agent_graph
from backend.agents.rag_agent import rag_agent_graph
from backend.agents.orchestrator import create_supervisor_node

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
        return "history_manager"
    return "unsafe_handler"

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("input_guardrail", check_input_guardrail_node)
    workflow.add_node("history_manager", summarize_history_node)
    workflow.add_node("unsafe_handler", handle_unsafe_input)
    workflow.add_node("output_guardrail", check_output_guardrail_node)
    supervisor_chain = create_supervisor_node()
    
    def supervisor_node(state: AgentState):
        decision = supervisor_chain.invoke(state)
        return {"next": decision.next}

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("TaskManager", react_agent_graph)
    workflow.add_node("KnowledgeBase", rag_agent_graph)
    workflow.add_edge(START, "input_guardrail")
    
    workflow.add_conditional_edges(
        "input_guardrail",
        route_guardrail,
        {
            "history_manager": "history_manager",
            "unsafe_handler": "unsafe_handler"
        }
    )
    
    workflow.add_edge("history_manager", "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x.get("next", "FINISH"),
        {
            "TaskManager": "TaskManager",
            "KnowledgeBase": "KnowledgeBase",
            "FINISH": "output_guardrail"
        }
    )
    
    workflow.add_edge("TaskManager", "supervisor")
    workflow.add_edge("KnowledgeBase", "supervisor")
    
    workflow.add_edge("unsafe_handler", "output_guardrail")
    workflow.add_edge("output_guardrail", END)
    
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)
    
    app = workflow.compile(checkpointer=memory)
    return app

agent_app = build_graph()
