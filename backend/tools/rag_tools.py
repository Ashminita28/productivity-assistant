from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type, Optional
from backend.services.rag_service import rag_service

class LearnDocumentInput(BaseModel):
    file_path: str = Field(..., description="The absolute or relative path to the PDF or text document to ingest.")

class LearnDocumentTool(BaseTool):
    name: str = "learn_document"
    description: str = (
        "Use this tool when the user asks you to read, learn, or ingest a document. "
        "It will chunk the document and store it in the knowledge base."
    )
    args_schema: Type[BaseModel] = LearnDocumentInput

    def _run(self, file_path: str) -> str:
        return rag_service.ingest_document(file_path)


class QueryKnowledgeBaseInput(BaseModel):
    query: str = Field(..., description="The specific question or search query to look up in the knowledge base.")
    filename: Optional[str] = Field(default=None, description="Optional. The exact name of the file to search within (e.g., 'react.pdf'). If provided, forces the database to ignore all other files.")

class QueryKnowledgeBaseTool(BaseTool):
    name: str = "query_knowledge_base"
    description: str = (
        "Use this tool to answer questions based on previously ingested documents. "
        "It performs a semantic search against the vector database and returns relevant text chunks."
    )
    args_schema: Type[BaseModel] = QueryKnowledgeBaseInput

    def _run(self, query: str, filename: Optional[str] = None) -> str:
        return rag_service.query_knowledge_base(query, filename=filename)
