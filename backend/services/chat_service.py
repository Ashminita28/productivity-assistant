from backend.agents.agent_graph import agent_app
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.types import Command
import json

class ChatService:
    def chat_sync(self, state_input: dict, config: dict) -> str:
        """Processes the chat synchronously."""
        result = agent_app.invoke(state_input, config=config)
        return result["response"]

    def stream_chat(self, state_input: dict, config: dict):
        """Streams the response tokens. Detects interrupt events and yields an approval request."""
        for chunk in agent_app.stream(state_input, config=config, stream_mode="values"):
            if "__interrupt__" in chunk:
                interrupt_value = chunk["__interrupt__"][0].value
                yield "\n\n" + json.dumps({
                    "requires_approval": True,
                    "prompt": interrupt_value
                })
                return  
            messages = chunk.get("messages", [])
            if messages:
                last = messages[-1]
                if isinstance(last, AIMessage) and last.content and isinstance(last.content, str):
                    yield last.content

    def respond_interrupt(self, approved: bool, config: dict):
        """Resumes the graph after human approval or rejection using Command(resume=...)."""
        decision = "Approve" if approved else "Reject"

        for chunk in agent_app.stream(Command(resume=decision), config=config, stream_mode="values"):
            messages = chunk.get("messages", [])
            if messages:
                last = messages[-1]
                if isinstance(last, AIMessage) and last.content and isinstance(last.content, str):
                    yield last.content
        

    def get_chat_history(self, thread_id: str):
        """Retrieves chat history from the checkpointer."""
        config = {"configurable": {"thread_id": thread_id}}
        state = agent_app.get_state(config)
        messages = state.values.get("messages", [])
        
        history = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage): 
                if msg.content:
                    history.append({"role": "assistant", "content": msg.content})
        return history
