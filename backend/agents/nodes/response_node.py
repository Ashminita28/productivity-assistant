from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from backend.config.env_config import settings
from backend.agents.state import AgentState
from backend.agents.prompts import RESPONSE_SYSTEM_PROMPT

def generate_response_node(state: AgentState) -> dict:
    """Takes the tool result and generates a friendly response."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=settings.LLM_API_KEY)
    
    prompt = RESPONSE_SYSTEM_PROMPT.format(
        user_input=state["user_input"],
        tool_result=state["tool_result"]
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "response": response.content,
        "messages": [AIMessage(content=response.content)]
    }
