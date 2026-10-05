from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from backend.states.agent_state import AgentState
import sqlite3
from langchain_core.runnables import RunnableConfig
from backend.guardrails.guardrails import check_input_guardrail_node, check_output_guardrail_node
from backend.nodes.history_manager import summarize_history_node
from langchain_core.messages import AIMessage
from backend.config.env_config import settings
from backend.agents.orchestrator import get_orchestrator_agent
from backend.agents.llm_factory import get_llm

def general_assistant_node(state: AgentState):
    """Handles general chit-chat when no specialized tools are needed."""
    llm = get_llm()
    sys_prompt = AIMessage(content="You are a helpful assistant. Keep your responses concise and friendly.")
    messages = state.get("messages", [])
    response = llm.invoke([sys_prompt] + messages)
    return {"messages": [response]}

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
    
    orchestrator_agent = get_orchestrator_agent()
    
    def orchestrator_node(state: AgentState, config: RunnableConfig):
        response = orchestrator_agent.invoke({"messages": state["messages"]}, config=config)
        return {"messages": response["messages"][-1:]}

    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_edge(START, "input_guardrail")
    
    workflow.add_conditional_edges(
        "input_guardrail",
        route_guardrail,
        {
            "history_manager": "history_manager",
            "unsafe_handler": "unsafe_handler"
        }
    )
    
    workflow.add_edge("history_manager", "orchestrator")
    workflow.add_edge("orchestrator", "output_guardrail")
    
    workflow.add_edge("unsafe_handler", "output_guardrail")
    workflow.add_edge("output_guardrail", END)
    
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    memory = SqliteSaver(conn)
    
    app = workflow.compile(checkpointer=memory)
    return app

agent_app = build_graph()
