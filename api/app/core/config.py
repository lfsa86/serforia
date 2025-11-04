"""
Configuration settings for the FastAPI application
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # Database Settings
    DB_SERVER: str = "localhost"
    DB_PORT: int = 1433
    DB_DATABASE: str = "SERFOR_BDDWH"
    DB_USERNAME: str = "sa"
    DB_PASSWORD: str
    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"
    DB_TRUST_CERT: str = "yes"

    # OpenAI Settings
    OPENAI_API_KEY: str

    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

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
