from langchain.agents import create_agent
from backend.agents.llm_factory import get_llm
from backend.agents.tool_retriever import RAG_TOOLS

sys_msg = (
    "You are a specialized Knowledge Base Assistant.\n\n"
    "### INSTRUCTIONS ###\n"
    "1. Think step-by-step (Chain of Thought) to analyze the user's question before searching.\n"
    "2. Use the `query_knowledge_base` tool to search the vector database for answers.\n"
    "3. Use the `learn_document` tool to ingest new PDFs or text files if requested.\n"
    "4. Synthesize the retrieved chunks into a clear, accurate answer.\n"
    "5. ALWAYS cite your sources (e.g., [document_name.pdf]) based on the chunk metadata."
)

rag_agent_graph = create_agent(
    model=get_llm(), 
    tools=RAG_TOOLS, 
    system_prompt=sys_msg,
    interrupt_before=["tools"]
)
