from langchain_core.prompts import ChatPromptTemplate

response_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful and polite Personal Productivity Assistant.
You have just executed an action for the user. 
Using the user's original request and the result of the tool execution, formulate a natural, friendly response.

User Request: {user_input}
Tool Result: {tool_result}

Response:"""),
    ("user", "{user_input}")
])
