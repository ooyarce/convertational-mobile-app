from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    properties_api_url: str
    properties_api_token: str

    # LLM
    llm_model: str = "gemini-2.5-flash"

    # HTTP
    request_timeout: float = 30.0

    model_config = {"env_file": ".env"}


settings = Settings()
