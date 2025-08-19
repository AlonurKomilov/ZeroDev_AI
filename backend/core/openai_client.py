from backend.core.settings import settings
from openai import AsyncOpenAI

# The client is initialized here, but the validation of the API key
# is moved to the adapter that actually uses it. This allows the application
# and tests to load without requiring the key to be present.
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
