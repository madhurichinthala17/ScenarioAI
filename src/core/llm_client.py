from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from src.config import settings
from src.core.exceptions import LLMError
from src.core.logger import get_logger

log = get_logger(__name__)


def _build_llm():
    """
    Factory that returns the right LangChain chat model based on LLM_PROVIDER.

    Lazy imports: each provider's package is only imported if that provider
    is actually selected. This means you don't need langchain_openai installed
    if you're only using Ollama, and vice versa.

    Both ChatOllama and ChatOpenAI are subclasses of BaseChatModel — they share
    the same .invoke() and .bind_tools() interface, so LLMClient.invoke() and
    invoke_with_tools() work identically regardless of which provider is chosen.
    """
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=settings.llm_model, temperature=settings.llm_temperature)

    elif provider == "openai":
        if not settings.openai_api_key:
            # Fail at startup with a clear message rather than 20s into the
            # pipeline when the first LLM call is attempted
            raise LLMError(
                "LLM_PROVIDER=openai but OPENAI_API_KEY is not set. "
                "Add it to your .env file or GitHub Secrets."
            )
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.openai_api_key,
        )

    else:
        raise LLMError(
            f"Unknown LLM_PROVIDER: '{settings.llm_provider}'. "
            "Supported values: ollama, openai"
        )


class LLMClient:
    def __init__(self):
        self.llm = _build_llm()
        log.info("LLM client ready (provider=%s, model=%s)", settings.llm_provider, settings.llm_model)

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        try:
            response = self.llm.invoke(messages)
        except LLMError:
            raise
        except Exception as e:
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
