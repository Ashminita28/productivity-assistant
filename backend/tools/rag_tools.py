from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from typing import Type, Optional
from backend.services.rag_service import rag_service


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
