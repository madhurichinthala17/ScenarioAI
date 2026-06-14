from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


class LLMClient:
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5", temperature=0)

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = self.llm.invoke(messages)
        return response.content

    def invoke_with_tools(self, system_prompt: str, user_prompt: str, tools: list) -> str:
        llm_with_tools = self.llm.bind_tools(tools)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        while True:
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            if not response.tool_calls:
                return response.content

            # Execute each tool the LLM decided to call
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # Find and execute the matching tool
                tool_fn = next(
                    (t for t in tools if t.name == tool_name), None
                )
                if tool_fn:
                    result = tool_fn.invoke(tool_args)
                    from langchain_core.messages import ToolMessage
                    messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        )
                    )