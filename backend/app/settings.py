from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str | None = None
    allowed_origins: List[str] = ["http://localhost:3000"]

    class Config:
        env_prefix = ""
        env_file = ".env"

settings = Settings()