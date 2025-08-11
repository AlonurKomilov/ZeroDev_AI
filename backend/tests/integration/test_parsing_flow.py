import pytest
import time
import json
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from backend.main import app
from backend.core import ai_router

import redis
from backend.core.settings import settings

# Helper to check for Redis availability before running integration tests
def is_redis_available():
    try:
        # Use the same settings as the application
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            socket_connect_timeout=1 # Quick timeout
        )
        r.ping()
        return True
    except redis.exceptions.ConnectionError:
        return False

@pytest.mark.integration
@pytest.mark.skipif(not is_redis_available(), reason="Redis server is not available")
def test_parsing_flow_e2e(monkeypatch):
    """
    Tests the full asynchronous parsing flow:
    1. POST to /parse to create a task.
    2. GET /tasks/{task_id} to poll for the result.
    3. Verifies the final result is correct.

    This test requires a running Redis instance for the Celery broker and result backend.
    """
    # 1. Mock the AI Router to avoid real LLM calls and return a predictable result
    mock_spec = {"project_name": "test-project", "description": "A test project", "targets": ["target1"]}

    # The mock response should mimic the structure of the adapter's return value
    mock_completion_result = {
        "choices": [{"message": {"content": json.dumps(mock_spec)}}]
    }

    # Create a mock adapter instance
    mock_adapter_instance = MagicMock()
    # The chat_completion method should be an async mock
    mock_adapter_instance.chat_completion = AsyncMock(return_value=mock_completion_result)

    # Monkeypatch the get_llm_adapter function to return our mock instance
    monkeypatch.setattr(ai_router, "get_llm_adapter", lambda model_name: mock_adapter_instance)

    client = TestClient(app)

    # 2. Call the /parse endpoint to start the task
    response = client.post("/parse", json={"prompt": "test prompt", "model_name": "gpt-4o-mini"})
    assert response.status_code == 202
    task_id = response.json().get("task_id")
    assert task_id

    # 3. Poll the /tasks/{task_id} endpoint until completion
    timeout = 30  # 30-second timeout for the test
    start_time = time.time()
    final_response = None
    while time.time() - start_time < timeout:
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        final_response = response.json()
        if final_response["status"] in ["SUCCESS", "FAILURE"]:
            break
        time.sleep(1) # Wait 1 second between polls

    # 4. Assert the final state of the task
    assert final_response is not None, "Polling for task result timed out."
    assert final_response["status"] == "SUCCESS", f"Task failed with result: {final_response.get('result')}"

    # The result of the task should be the dictionary version of the spec
    assert final_response["result"] == mock_spec
