import os
import logging
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from backend.agents.llm_factory import get_embeddings
from backend.config.env_config import settings

logger = logging.getLogger("productivityAssistant")

class RAGService:
    def __init__(self):
       
        self.persist_directory = os.path.join(os.getcwd(), "data", "qdrant_db")
        os.makedirs(self.persist_directory, exist_ok=True)
        
      
        self.embeddings = get_embeddings()
        
    
        self.client = QdrantClient(path=self.persist_directory)
        
        
        if not self.client.collection_exists("knowledge_base"):
            from qdrant_client.http.models import Distance, VectorParams
            self.client.create_collection(
                collection_name="knowledge_base",
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
            )
        
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name="knowledge_base",
            embedding=self.embeddings,
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200,
            length_function=len
        )
        
        logger.info(f"RAG Service initialized. Vector DB at: {self.persist_directory}")

    def ingest_document(self, file_path: str) -> str:
        """Loads a document, chunks it, and stores it in the vector database."""
        if not os.path.exists(file_path):
            return f"Error: Document not found at path {file_path}"
            
        try:
            logger.info(f"Ingesting document: {file_path}")
            
           
            if file_path.lower().endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            else:
               
                loader = TextLoader(file_path)
                
            documents = loader.load()
            
            if not documents:
                return "Error: Document loaded but contained no readable text."
                
            chunks = self.text_splitter.split_documents(documents)
            
            
            self.vector_store.add_documents(chunks)
            
            return f"Successfully ingested document '{os.path.basename(file_path)}'. Split into {len(chunks)} chunks."
            
        except Exception as e:
            logger.error(f"Failed to ingest document {file_path}: {str(e)}")
            return f"Error ingesting document: {str(e)}"

    def query_knowledge_base(self, query: str, k: int = 3) -> str:
        """Searches the vector database for relevant chunks."""
        try:
            logger.info(f"Querying knowledge base for: '{query}'")
            
            results = self.vector_store.similarity_search(query, k=k)
            
            if not results:
                return "No relevant information found in the knowledge base."
                
           
            formatted_results = []
            for i, res in enumerate(results):
                source = res.metadata.get("source", "Unknown Source")
                page = res.metadata.get("page", "N/A")
                formatted_results.append(
                    f"--- Source: {source} (Page: {page}) ---\n{res.page_content}"
                )
                
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"Failed to query knowledge base: {str(e)}")
            return f"Error querying knowledge base: {str(e)}"


rag_service = RAGService()
