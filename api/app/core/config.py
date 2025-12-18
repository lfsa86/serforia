"""
Configuration settings for the FastAPI application
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

# Load encrypted env if available (for QA/Production)
_env_encryption_key = os.environ.get('ENV_ENCRYPTION_KEY')
_encrypted_env_path = Path(__file__).parent.parent.parent / '.env.encrypted'

if _env_encryption_key and _encrypted_env_path.exists():
    from utils.env_crypto import inject_encrypted_env
    inject_encrypted_env(str(_encrypted_env_path), _env_encryption_key)


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # Database Settings (from .env)
    DB_SERVER: str
    DB_PORT: int = 1433
    DB_DATABASE: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"
    DB_TRUST_CERT: str = "yes"

    # OpenAI Settings
    OPENAI_API_KEY: str

    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # SGI Seguridad Settings (from .env)
    SGI_BASE_URL: str
    SGI_SISTEMA_ID: int
    SGI_COMPAGNIA_ID: int

    # Auth Dev Mode (bypass para desarrollo)
    AUTH_DEV_MODE: bool = False
    AUTH_DEV_USER: str = "dev_user"
    AUTH_DEV_PASSWORD: str = "dev123"
    AUTH_FALLBACK_ON_ERROR: bool = False

    # JWT Settings (from .env)
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 2

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def database_url(self) -> str:
        """Construct database connection string"""
        trust_cert = "yes" if self.DB_TRUST_CERT.lower() in ["yes", "true", "1"] else "no"
        return (
            f"DRIVER={{{self.DB_DRIVER}}};"
            f"SERVER={self.DB_SERVER},{self.DB_PORT};"
            f"DATABASE={self.DB_DATABASE};"
            f"UID={self.DB_USERNAME};"
            f"PWD={self.DB_PASSWORD};"
            f"TrustServerCertificate={trust_cert};"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
