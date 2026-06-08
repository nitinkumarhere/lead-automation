from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = "mock-key"
    API_BEARER_TOKEN: str = "super-secret-n8n-token"

    class Config:
        env_file = ".env"

settings = Settings()
