import os
import pytest
from backend.core.settings import Settings

@pytest.mark.unit
def test_settings_load_from_env(monkeypatch):
    """
    Test that the Settings class correctly loads values from environment variables.
    """
    # Use monkeypatch to temporarily set environment variables
    monkeypatch.setenv("TESTING", "True")
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    monkeypatch.setenv("REDIS_HOST", "testhost")
    monkeypatch.setenv("REDIS_PORT", "1234")
    monkeypatch.setenv("REDIS_DB", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")
    monkeypatch.setenv("JWT_SECRET", "test_secret")
    monkeypatch.setenv("ENCRYPTION_KEY", "-0y53Tfnc9dmHei5tfnr3asC1n4hAi1fkiUY59Fv__I=")
    monkeypatch.setenv("OWNER_EMERGENCY_KEY", "test_emergency_key")


    # Instantiate the settings class, which should trigger it to load from the env
    # We must create a new instance to force re-reading of env vars
    settings = Settings(_env_file=None) # Pass None to prevent loading a .env file

    assert settings.APP_NAME == "Test App"
    assert settings.DEBUG is True
    assert settings.REDIS_HOST == "testhost"
    assert settings.REDIS_PORT == 1234
    assert settings.REDIS_URL == "redis://testhost:1234/1"
    assert settings.OPENAI_API_KEY == "test_key"
