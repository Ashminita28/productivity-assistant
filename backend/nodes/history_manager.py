from langchain_core.messages import RemoveMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from backend.agents.llm_factory import get_llm
from backend.states.agent_state import AgentState
import logging

logger = logging.getLogger("productivityAssistant")

def summarize_history_node(state: AgentState) -> dict:
    messages = state.get("messages", [])
    current_summary = state.get("summary", "")
    
    
    if len(messages) <= 6:
        return {} 
        
    logger.info(f"Conversation history is {len(messages)} messages long. Compressing...")
    
    messages_to_summarize = messages[:-2]
    
    
    history_text = ""
    for m in messages_to_summarize:
        role = "User" if isinstance(m, HumanMessage) else "Assistant"
        content = m.content if hasattr(m, "content") else str(m)
        history_text += f"{role}: {content}\n"
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a conversation summarization AI. Summarize the following chat history in a concise paragraph. If there is a 'Previous Summary', incorporate it seamlessly into the new summary. Focus ONLY on important context, user preferences, or facts."),
        ("user", "Previous Summary: {current_summary}\n\nNew Chat History to Summarize:\n{history_text}")
    ])
    
    llm = get_llm(task_type="fast")
    chain = prompt | llm
    
    try:
        new_summary_msg = chain.invoke({
            "current_summary": current_summary, 
            "history_text": history_text
        })
        new_summary = new_summary_msg.content
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        return {} 
        
    
    delete_messages = [RemoveMessage(id=m.id) for m in messages_to_summarize if m.id]
    
    logger.info("Successfully compressed history and generated rolling summary.")
    return {
        "summary": new_summary,
        "messages": delete_messages
    }
