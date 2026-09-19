from langchain.agents import create_agent
from backend.agents.llm_factory import get_llm
from backend.agents.tool_retriever import ALL_TOOLS

react_agent_graph = create_agent(model=get_llm(), tools=ALL_TOOLS, interrupt_before=["tools"])
