from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str | None = None
    allowed_origins: str = "http://localhost:3000"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_bucket_name: str | None = None
    aws_region: str = "us-east-1"
    locationiq_api_key: str | None = None

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_prefix = ""
        env_file = ".env"

settings = Settings()