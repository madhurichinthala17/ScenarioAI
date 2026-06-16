from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from src.config import settings
from src.core.exceptions import LLMError
from src.core.logger import get_logger

log = get_logger(__name__)


class LLMClient:
    def __init__(self):
        # model and temperature now come from config, not hardcoded here
        self.llm = ChatOllama(model=settings.llm_model, temperature=settings.llm_temperature)
        log.info("LLM client ready (model=%s)", settings.llm_model)

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        try:
            response = self.llm.invoke(messages)
        except Exception as e:
            # wrap so callers only need to handle LLMError, not every possible network error
            raise LLMError(f"LLM call failed: {e}") from e
        return response.content

    def invoke_with_tools(self, system_prompt: str, user_prompt: str, tools: list) -> str:
        llm_with_tools = self.llm.bind_tools(tools)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            while True:
                response = llm_with_tools.invoke(messages)
                messages.append(response)

                if not response.tool_calls:
                    return response.content

                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    log.debug("Tool call: %s(%s)", tool_name, tool_args)

                    tool_fn = next((t for t in tools if t.name == tool_name), None)
                    if tool_fn:
                        result = tool_fn.invoke(tool_args)
                        messages.append(
                            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                        )
        except LLMError:
            raise
        except Exception as e:
            raise LLMError(f"LLM tool call failed: {e}") from e
