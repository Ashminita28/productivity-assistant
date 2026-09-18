import logging
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.config.env_config import settings
from backend.tools.task_tools import (
    AddTaskTool, ListTasksTool, UpdateTaskTool, 
    DeleteTaskTool, SummarizeTasksTool
)
from langchain_core.documents import Document

logger = logging.getLogger("productivityAssistant")

ALL_TOOLS = [
    AddTaskTool(), ListTasksTool(), UpdateTaskTool(), 
    DeleteTaskTool(), SummarizeTasksTool()
]


try:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.GOOGLE_API_KEY
    )
    vector_store = InMemoryVectorStore(embedding=embeddings)

    documents = []
    for tool in ALL_TOOLS:
        content = f"Tool Name: {tool.name}\nDescription: {tool.description}"
        documents.append(Document(page_content=content, metadata={"tool_name": tool.name}))

    vector_store.add_documents(documents)
    logger.info("Semantic Tool Retriever successfully initialized.")
    is_vector_store_ready = True
except Exception as e:
    logger.error(f"Failed to build tool embeddings: {e}")
    is_vector_store_ready = False

def get_relevant_tools(query: str, k: int = 3):
    """Semantically search for the most relevant tools based on user input."""
    if not is_vector_store_ready:
        return ALL_TOOLS
        
    try:
        results = vector_store.similarity_search(query, k=k)
        relevant_tool_names = {doc.metadata["tool_name"] for doc in results}
        matched_tools = [tool for tool in ALL_TOOLS if tool.name in relevant_tool_names]
        logger.info(f"Semantic Search matched tools: {[t.name for t in matched_tools]}")
        
        if not any(t.name == "list_tasks" for t in matched_tools):
            matched_tools.append(ListTasksTool())
            
        return matched_tools
    except Exception as e:
        logger.warning(f"Semantic tool search failed, falling back to all tools: {e}")
        return ALL_TOOLS
