import os
import pytest
from backend.core.settings import Settings

@pytest.mark.unit
def test_settings_load_from_env(monkeypatch):
    """
    Test that the Settings class correctly loads values from environment variables.
    """
    # Use monkeypatch to temporarily set environment variables
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("REDIS_HOST", "testhost")
    monkeypatch.setenv("REDIS_PORT", "1234")
    monkeypatch.setenv("OPENAI_API_KEY", "test_key")

    # Instantiate the settings class, which should trigger it to load from the env
    # We must create a new instance to force re-reading of env vars
    settings = Settings(_env_file=None) # Pass None to prevent loading a .env file

    assert settings.APP_NAME == "Test App"
    assert settings.DEBUG is True
    assert settings.REDIS_HOST == "testhost"
    assert settings.REDIS_PORT == 1234
    assert settings.REDIS_URL == "redis://testhost:1234/0"
    assert settings.OPENAI_API_KEY == "test_key"

@pytest.mark.unit
def test_settings_default_values(monkeypatch):
    """
    Test that the Settings class uses default values when no env vars are set.
    """
    # Ensure no relevant env vars are set by monkeypatching them away
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("REDIS_HOST", raising=False)
    monkeypatch.delenv("REDIS_PORT", raising=False)

    # Create a new instance to ensure we get defaults
    settings = Settings(_env_file=None)

    assert settings.APP_NAME == "ZeroDev Backend"
    assert settings.DEBUG is False
    assert settings.REDIS_HOST == "localhost"
    assert settings.REDIS_PORT == 6379
