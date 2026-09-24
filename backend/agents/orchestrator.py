from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.agents.llm_factory import get_llm

class RouterDecision(BaseModel):
    next: Literal["FINISH", "TaskManager", "KnowledgeBase"] = Field(
        description="The next agent to route to, or FINISH if the request is complete or unhandled."
    )

def create_supervisor_node():
    options = ["FINISH", "TaskManager", "KnowledgeBase"]
    
    system_prompt = (
        "You are the Supervisor Orchestrator managing two specialized worker agents: \n"
        "1. 'TaskManager': Responsible for creating, updating, listing, summarizing, searching, and deleting tasks and todos.\n"
        "2. 'KnowledgeBase': Responsible for ingesting PDFs/documents and answering questions based on the document knowledge base.\n\n"
        "Your job is to read the conversation and decide who should act next.\n"
        "- If the user wants to interact with tasks/todos, route to 'TaskManager'.\n"
        "- If the user wants to read a PDF or ask questions about a PDF/document, route to 'KnowledgeBase'.\n"
        "- If the workers have successfully completed the user's request, or if the user is just saying hello, route to 'FINISH'."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}")
    ]).partial(options=str(options))
    
   
    supervisor_chain = prompt | get_llm().with_structured_output(RouterDecision)
    
    return supervisor_chain
