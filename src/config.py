from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_model: str = "qwen2.5"
    llm_temperature: float = 0.0
    max_retries: int = 2
    output_dir: str = "generated_tests"

    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "scenarioai"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
