from backend.agents.agent_graph import agent_app
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json

class ChatService:
    def chat_sync(self, state_input: dict, config: dict) -> str:
        """Processes the chat synchronously."""
        result = agent_app.invoke(state_input, config=config)
        return result["response"]

    def stream_chat(self, state_input: dict, config: dict):
        """Streams the response tokens and smartly handles tool interruptions."""
        input_data = state_input
        while True:
            for msg, metadata in agent_app.stream(input_data, config=config, stream_mode="messages"):
                if metadata.get("langgraph_node") in ["react_agent", "agent", "TaskManager", "KnowledgeBase", "unsafe_handler", "output_guardrail"]:
                    if msg.content and isinstance(msg.content, str):
                        yield msg.content

            state = agent_app.get_state(config)
            sub_state = agent_app.get_state(config, subgraphs=True)
            
            is_waiting = False
            last_msg = None
            
            if sub_state and hasattr(sub_state, "tasks"):
                for task in sub_state.tasks:
                    if task.state and "tools" in task.state.next:
                        is_waiting = True
                        last_msg = task.state.values.get("messages", [])[-1]
                        break
            
            if is_waiting and last_msg and hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
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
                if not state.next:
                    break
                else:
                    input_data = None

    def respond_interrupt(self, approved: bool, config: dict):
        """Resumes the graph after human approval or rejection."""
        sub_state = agent_app.get_state(config, subgraphs=True)
        target_config = None
        last_msg = None
        
        if sub_state and hasattr(sub_state, "tasks"):
            for task in sub_state.tasks:
                if task.state and "tools" in task.state.next:
                    target_config = task.state.config
                    last_msg = task.state.values.get("messages", [])[-1]
                    break
                    
        if not target_config:
            return
            
        if approved:
            input_data = None
        else:
            tool_messages = []
            for tc in last_msg.tool_calls:
                tool_messages.append(ToolMessage(
                    tool_call_id=tc["id"], 
                    content="Error: The user rejected this action. Apologize and ask what else to do.",
                    name=tc["name"]
                ))

            agent_app.update_state(target_config, {"messages": tool_messages}, as_node="tools")
            input_data = None
            
        for msg, metadata in agent_app.stream(input_data, config=config, stream_mode="messages"):
            if metadata.get("langgraph_node") in ["react_agent", "agent", "TaskManager", "KnowledgeBase"]:
                if msg.content and isinstance(msg.content, str):
                    yield msg.content
        

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
