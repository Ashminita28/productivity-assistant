from backend.agents.agent_graph import agent_app
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json

class ChatService:
    def chat_sync(self, state_input: dict, config: dict) -> str:
        """Processes the chat synchronously."""
        result = agent_app.invoke(state_input, config=config)
        return result["response"]

    async def stream_chat(self, state_input: dict, config: dict):
        """Streams the response tokens and smartly handles tool interruptions."""
        input_data = state_input
        while True:
            async for event in agent_app.astream_events(input_data, config=config, version="v2"):
                kind = event["event"]
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"].content
                    if chunk and isinstance(chunk, str):
                        yield chunk

            state = agent_app.get_state(config)
            if not state.next:
                break 
                
            if "tools" in state.next:
                last_msg = state.values.get("messages", [])[-1]
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    destructive_calls = [tc for tc in last_msg.tool_calls if tc["name"] in ["delete_task", "update_task"]]
                    if destructive_calls:
                        yield "\n\n" + json.dumps({
                            "requires_approval": True,
                            "tool": destructive_calls[0]["name"],
                            "args": destructive_calls[0]["args"]
                        })
                        break 
                    else:
                        input_data = None
                else:
                    break
            else:
                break

    async def respond_interrupt(self, approved: bool, config: dict):
        """Resumes the graph after human approval or rejection."""
        state = agent_app.get_state(config)
        if not state.next or "tools" not in state.next:
            return
            
        if approved:
            input_data = None
        else:
            last_msg = state.values.get("messages", [])[-1]
            tool_messages = []
            for tc in last_msg.tool_calls:
                tool_messages.append(ToolMessage(
                    tool_call_id=tc["id"], 
                    content="Error: The user rejected this action. Apologize and ask what else to do.",
                    name=tc["name"]
                ))

            agent_app.update_state(config, {"messages": tool_messages}, as_node="tools")
            input_data = None
            
        async for event in agent_app.astream_events(input_data, config=config, version="v2"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"].content
                if chunk and isinstance(chunk, str):
                    yield chunk
        
        history = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage): 
                if msg.content:
                    history.append({"role": "assistant", "content": msg.content})
        return history
