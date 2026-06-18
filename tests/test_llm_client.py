"""
Tests for LLMClient provider selection.
Tests the factory logic and startup error handling — not actual LLM calls.
"""
from unittest.mock import patch, MagicMock
import pytest
from src.core.exceptions import LLMError


def _make_settings(provider: str, model: str = "test-model", api_key: str = ""):
    """Helper: build a mock settings object with the given provider config."""
    s = MagicMock()
    s.llm_provider = provider
    s.llm_model = model
    s.llm_temperature = 0.0
    s.openai_api_key = api_key
    return s


def test_unknown_provider_raises_llm_error():
    # If someone sets LLM_PROVIDER=groq (not supported yet), fail at startup
    # with a clear message rather than a cryptic AttributeError later
    with patch("src.core.llm_client.settings", _make_settings("groq")):
        from src.core.llm_client import _build_llm
        with pytest.raises(LLMError, match="Unknown LLM_PROVIDER"):
            _build_llm()


def test_openai_without_api_key_raises_llm_error():
    # LLM_PROVIDER=openai with no API key → clear error immediately at startup,
    # not after 20s when the first LLM call is attempted
    with patch("src.core.llm_client.settings", _make_settings("openai", api_key="")):
        from src.core.llm_client import _build_llm
        with pytest.raises(LLMError, match="OPENAI_API_KEY is not set"):
            _build_llm()


def test_ollama_provider_builds_chat_ollama():
    # When provider=ollama, _build_llm should instantiate ChatOllama with
    # the model and temperature from settings
    mock_chat_ollama = MagicMock()
    mock_ollama_module = MagicMock()
    mock_ollama_module.ChatOllama = mock_chat_ollama

    with patch("src.core.llm_client.settings", _make_settings("ollama", model="qwen2.5")):
        with patch.dict("sys.modules", {"langchain_ollama": mock_ollama_module}):
            from src.core.llm_client import _build_llm
            _build_llm()
            mock_chat_ollama.assert_called_once_with(model="qwen2.5", temperature=0.0)


def test_openai_provider_builds_chat_openai():
    # When provider=openai with a key set, _build_llm should instantiate ChatOpenAI
    mock_chat_openai = MagicMock()
    mock_openai_module = MagicMock()
    mock_openai_module.ChatOpenAI = mock_chat_openai

    with patch("src.core.llm_client.settings", _make_settings("openai", model="gpt-4o-mini", api_key="sk-test")):
        with patch.dict("sys.modules", {"langchain_openai": mock_openai_module}):
            from src.core.llm_client import _build_llm
            _build_llm()
            mock_chat_openai.assert_called_once_with(
                model="gpt-4o-mini",
                temperature=0.0,
                api_key="sk-test",
            )
