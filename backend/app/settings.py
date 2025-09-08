from pydantic_settings import BaseSettings
from typing import List, Dict, Any
from datetime import datetime

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str | None = None
    allowed_origins: str = "http://localhost:3000"
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_bucket_name: str | None = None
    aws_region: str = "us-east-1"
    locationiq_api_key: str | None = None
    db_init_mode: str | None = None

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def user_profile(self) -> Dict[str, Any]:
        """Hardcoded user profile for demo purposes"""
        return {
            "name": "Alex Chen",
            "birth_date": "1992-03-15",
            "age": datetime.now().year - 1992,
            "city": "San Francisco",
            "state": "California", 
            "occupation": "Software Engineer",
            "interests": ["hiking", "photography", "cooking", "travel"],
            "relationships": {
                "partner": "Sam",
                "pets": ["Luna (cat)"]
            }
        }

    class Config:
        env_prefix = ""
        env_file = ".env"

settings = Settings()