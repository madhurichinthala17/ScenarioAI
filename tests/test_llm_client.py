"""
Tests for LLMClient provider selection.
These test the factory logic and error handling — not the actual LLM calls.
"""
from unittest.mock import patch, MagicMock
import pytest
from src.core.exceptions import LLMError


def test_unknown_provider_raises_llm_error():
    # If someone sets LLM_PROVIDER=groq (not supported yet), they should get
    # a clear error at startup, not a confusing AttributeError later
    with patch("src.core.llm_client.settings") as mock_settings:
        mock_settings.llm_provider = "groq"
        mock_settings.openai_api_key = ""
        from src.core.llm_client import _build_llm
        with pytest.raises(LLMError, match="Unknown LLM_PROVIDER"):
            _build_llm()


def test_openai_without_api_key_raises_llm_error():
    # If LLM_PROVIDER=openai but OPENAI_API_KEY is missing, fail immediately
    # with a human-readable message — not after 20s when the first call is made
    with patch("src.core.llm_client.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        mock_settings.openai_api_key = ""
        from src.core.llm_client import _build_llm
        with pytest.raises(LLMError, match="OPENAI_API_KEY is not set"):
            _build_llm()


def test_ollama_provider_builds_chat_ollama():
    # When provider=ollama, _build_llm should return a ChatOllama instance
    with patch("src.core.llm_client.settings") as mock_settings:
        mock_settings.llm_provider = "ollama"
        mock_settings.llm_model = "qwen2.5"
        mock_settings.llm_temperature = 0.0
        mock_settings.openai_api_key = ""

        mock_ollama = MagicMock()
        with patch.dict("sys.modules", {"langchain_ollama": MagicMock(ChatOllama=mock_ollama)}):
            from importlib import reload
            import src.core.llm_client as llm_mod
            reload(llm_mod)
            llm_mod._build_llm()
            mock_ollama.assert_called_once_with(model="qwen2.5", temperature=0.0)
