from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── LLM provider ──────────────────────────────────────────────────────
    # "ollama" uses a local Ollama instance (no API key needed)
    # "openai" uses the OpenAI API (requires OPENAI_API_KEY)
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5"
    llm_temperature: float = 0.0

    # Set when llm_provider=openai — reads from OPENAI_API_KEY env var
    openai_api_key: str = ""

    # ── Pipeline ──────────────────────────────────────────────────────────
    max_retries: int = 2
    output_dir: str = "generated_tests"

    # ── LangSmith tracing ──────────────────────────────────────
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "scenarioai"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
