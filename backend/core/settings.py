import os
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Centralized application settings.
    Settings are loaded from environment variables, a .env file, or a secrets manager.
    """
    TESTING: bool = False
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=os.environ.get("ENV_FILE", ".env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # Core settings
    APP_NAME: str = "ZeroDev Backend"
    DEBUG: bool = False

    # Database settings
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    # Redis settings
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_DB: Optional[int] = None

    # Celery settings - allow them to be None initially
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # OpenAI API Key
    OPENAI_API_KEY: Optional[str] = None

    # Security settings
    JWT_SECRET: Optional[str] = None
    ENCRYPTION_KEY: Optional[str] = None
    OWNER_EMERGENCY_KEY: Optional[str] = None

    VAULT_ADDR: Optional[str] = None
    VAULT_TOKEN: Optional[str] = None

    def __init__(self, **values):
        super().__init__(**values)
        if self.ENVIRONMENT == "production":
            from backend.core.secrets_manager import get_secrets_manager
            secrets_manager = get_secrets_manager()
            self.DATABASE_URL = secrets_manager.get_secret("DATABASE_URL")
            self.REDIS_HOST = secrets_manager.get_secret("REDIS_HOST")
            self.REDIS_PORT = int(secrets_manager.get_secret("REDIS_PORT"))
            self.REDIS_DB = int(secrets_manager.get_secret("REDIS_DB"))
            self.OPENAI_API_KEY = secrets_manager.get_secret("OPENAI_API_KEY")
            self.JWT_SECRET = secrets_manager.get_secret("JWT_SECRET")
            self.ENCRYPTION_KEY = secrets_manager.get_secret("ENCRYPTION_KEY")
            self.OWNER_EMERGENCY_KEY = secrets_manager.get_secret("OWNER_EMERGENCY_KEY")
        else:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    @property
    def REDIS_URL(self) -> str:
        """Constructs the Redis URL from its components."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @model_validator(mode='after')
    def set_celery_defaults(self) -> 'Settings':
        """
        Set default Celery URLs based on Redis settings if they are not provided.
        This runs after the other fields have been loaded and validated.
        """
        if self.CELERY_BROKER_URL is None:
            self.CELERY_BROKER_URL = self.REDIS_URL

        if self.CELERY_RESULT_BACKEND is None:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL
        return self

settings = Settings()
