from config.validate_env import validate_env

def test_env_check(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
    validate_env()  # Bu exception tashlamasligi kerak
