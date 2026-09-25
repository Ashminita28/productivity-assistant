from langchain.agents import create_agent
from backend.agents.llm_factory import get_llm
from backend.agents.tool_retriever import RAG_TOOLS

sys_msg = (
    "You are a specialized Knowledge Base Assistant. "
    "Your ONLY job is to help the user learn from documents and answer questions based on the knowledge base. "
    "Use the `learn_document` tool to ingest new PDFs or text files. "
    "Use the `query_knowledge_base` tool to search for answers. "
    "Always cite your sources if possible based on the chunk metadata."
)

rag_agent_graph = create_agent(
    model=get_llm(), 
    tools=RAG_TOOLS, 
    system_prompt=sys_msg,
    interrupt_before=["tools"]
)
