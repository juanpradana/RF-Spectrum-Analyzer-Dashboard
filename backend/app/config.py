from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./rf_analyzer.db"
    UPLOAD_DIR: str = "./uploads"
    REPORTS_DIR: str = "./reports"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    AUTH_USERNAME: str = "admin"
    AUTH_PASSWORD: str = "changeme123"
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.REPORTS_DIR, exist_ok=True)

settings = Settings()
