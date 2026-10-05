from langchain.agents import create_agent
from backend.agents.llm_factory import get_llm
from backend.agents.tool_retriever import ALL_TOOLS

sys_msg = (
    "You are a specialized Task Management Assistant.\n\n"
    "### INSTRUCTIONS ###\n"
    "1. Think step-by-step (Chain of Thought) about the user's request.\n"
    "2. Determine which tool is needed to accomplish the task (add, delete, update, list, search).\n"
    "3. Execute the tool and confirm the result to the user clearly and concisely.\n"
)

react_agent_graph = create_agent(model=get_llm(), tools=ALL_TOOLS, system_prompt=sys_msg)
