from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from backend.agents.react_agent import react_agent_graph
from backend.agents.rag_agent import rag_agent_graph
from langchain_core.messages import HumanMessage

class AgentInput(BaseModel):
    query: str = Field(..., description="The user's original query or specific command to send to the specialized agent.")

class TaskAgentTool(BaseTool):
    name: str = "task_agent"
    description: str = "Delegates task management operations (create, update, list, delete, search tasks) to the specialized Task Agent."
    args_schema: type[BaseModel] = AgentInput

    def _run(self, query: str) -> str:
        response = react_agent_graph.invoke({"messages": [HumanMessage(content=query)]})
        return response["messages"][-1].content

class RAGAgentTool(BaseTool):
    name: str = "rag_agent"
    description: str = "Delegates factual questions, document searches, and knowledge retrieval to the specialized RAG Agent."
    args_schema: type[BaseModel] = AgentInput

    def _run(self, query: str) -> str:
        response = rag_agent_graph.invoke({"messages": [HumanMessage(content=query)]})
        return response["messages"][-1].content
