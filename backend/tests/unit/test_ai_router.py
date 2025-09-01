from unittest.mock import MagicMock

import pytest
from backend.core import ai_router
from backend.core.ai_router import get_llm_adapter


@pytest.mark.unit
@pytest.mark.parametrize(
    "model_name, expected_adapter_class_name",
    [
        ("gpt-4o-mini", "OpenAIAdapter"),
        ("gpt-4", "OpenAIAdapter"),
        ("claude-3-opus-20240229", "ClaudeMockAdapter"),
        ("claude-2.1", "ClaudeMockAdapter"),
        ("some-other-model", "OpenAIAdapter"),  # Test the fallback case
        ("GPT-3.5-TURBO", "OpenAIAdapter"),  # Test case insensitivity
    ],
)
def test_get_llm_adapter_routing(monkeypatch, model_name, expected_adapter_class_name):
    """
    Test that the get_llm_adapter function routes to the correct adapter class
    without actually instantiating the real adapters.
    """
    # Mock the adapter classes in the ai_router module to prevent their __init__ from running
    mock_openai_class = MagicMock()
    mock_claude_class = MagicMock()

    monkeypatch.setattr(ai_router, "OpenAIAdapter", mock_openai_class)
    monkeypatch.setattr(ai_router, "ClaudeMockAdapter", mock_claude_class)

    # Call the router function
    get_llm_adapter(model_name)

    # Assert that the correct mock class was called (instantiated)
    if expected_adapter_class_name == "OpenAIAdapter":
        assert mock_openai_class.called, "OpenAIAdapter should have been instantiated"
        assert (
            not mock_claude_class.called
        ), "ClaudeMockAdapter should not have been instantiated"
    elif expected_adapter_class_name == "ClaudeMockAdapter":
        assert (
            not mock_openai_class.called
        ), "OpenAIAdapter should not have been instantiated"
        assert (
            mock_claude_class.called
        ), "ClaudeMockAdapter should have been instantiated"
