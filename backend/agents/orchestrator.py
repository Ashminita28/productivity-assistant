from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.agents.llm_factory import get_llm

class RouterDecision(BaseModel):
    next: Literal["FINISH", "TaskManager", "KnowledgeBase", "GeneralAssistant"] = Field(
        description="The next agent to route to, or FINISH if the request is complete."
    )

def create_supervisor_node():
    options = ["FINISH", "TaskManager", "KnowledgeBase", "GeneralAssistant"]
    
    system_prompt = (
        "You are the Supervisor Orchestrator managing two specialized worker agents: \n"
        "1. 'TaskManager': Responsible for creating, updating, listing, summarizing, searching, and deleting tasks and todos.\n"
        "2. 'KnowledgeBase': Responsible for ingesting PDFs/documents and answering questions based on the document knowledge base.\n\n"
        "Your job is to read the conversation and decide which specialized agent matches the user's intent.\n"
        "- TaskManager Intent: The user wants to manage, create, list, delete, or search their to-do list tasks.\n"
        "- KnowledgeBase Intent: The user is asking a factual question, requesting information from a document, or looking up knowledge/experience.\n"
        "- GeneralAssistant Intent: The user is just saying hello, making casual conversation, or asking generic questions unrelated to tasks or documents.\n"
        "- FINISH Intent: The specialized agents have already answered the user's question, and the turn is complete."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}")
    ]).partial(options=str(options))
    
   
    supervisor_chain = prompt | get_llm().with_structured_output(RouterDecision)
    
    return supervisor_chain
