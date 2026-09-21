import logging
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from backend.agents.llm_factory import get_embeddings
from backend.services.task_service import TaskService

logger = logging.getLogger("productivityAssistant")
vector_store = InMemoryVectorStore(get_embeddings())
_index_ready = False

def sync_task_index():
    """Fetches all tasks from the DB and recreates the semantic index."""
    global vector_store
    global _index_ready
    
    service = TaskService()
    tasks = service.get_all_tasks()
    
    vector_store = InMemoryVectorStore(get_embeddings())
    
    docs = []
    for t in tasks:
        
        docs.append(Document(
            page_content=t.description,
            metadata={"id": t.id, "status": t.status}
        ))
        
    if docs:
        vector_store.add_documents(docs)
        
    logger.info(f"Synced {len(docs)} tasks to the semantic vector store.")
    _index_ready = True

def invalidate_task_index():
    """Flags the index as stale so it gets rebuilt on the next search."""
    global _index_ready
    _index_ready = False

def search_tasks(query: str, k: int = 5):
    """Performs cosine similarity search against tasks"""
    global _index_ready
    if not _index_ready:
        sync_task_index()
        
    try:
        results = vector_store.similarity_search(query, k=k)
        
        
        query_words = set(query.lower().split())
        scored_results = []
        for d in results:
            content_words = set(d.page_content.lower().split())
            overlap = len(query_words.intersection(content_words))
            scored_results.append((overlap, d))
            
       
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        return [{"id": d.metadata["id"], "description": d.page_content, "status": d.metadata["status"]} for score, d in scored_results]
    except Exception as e:
        logger.warning(f"Semantic task search failed: {e}")
        return []
