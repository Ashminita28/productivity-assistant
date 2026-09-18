from backend.agents.agent_graph import agent_app
from langchain_core.messages import HumanMessage, AIMessage

class ChatService:
    def chat_sync(self, state_input: dict, config: dict) -> str:
        """Processes the chat synchronously."""
        result = agent_app.invoke(state_input, config=config)
        return result["response"]

    async def stream_chat(self, state_input: dict, config: dict):
        """Streams the response tokens natively from the LangGraph agent."""
        async for event in agent_app.astream_events(state_input, config=config, version="v2"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk and isinstance(chunk, str):
                    yield chunk

    def get_chat_history(self, thread_id: str) -> list:
        """Retrieves chat history from LangGraph's SQLite memory."""
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
