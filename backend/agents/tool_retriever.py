import logging
from langchain_core.vectorstores import InMemoryVectorStore

from backend.tools.task_tools import (
    AddTaskTool, ListTasksTool, UpdateTaskTool, 
    DeleteTaskTool, SummarizeTasksTool, SearchTaskTool
)
from langchain_core.documents import Document

logger = logging.getLogger("productivityAssistant")

ALL_TOOLS = [
    AddTaskTool(), ListTasksTool(), UpdateTaskTool(), 
    DeleteTaskTool(), SummarizeTasksTool(), SearchTaskTool()
]


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
