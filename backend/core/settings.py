from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Centralized application settings.
    Settings are loaded from environment variables and/or a .env file.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Core settings
    APP_NAME: str = "ZeroDev Backend"
    DEBUG: bool = False

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Celery settings - allow them to be None initially
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # OpenAI API Key
    OPENAI_API_KEY: str = "your_openai_api_key_here"

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
