import asyncio
from typing import Any, Callable, Coroutine

from tenacity import (
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)

from backend.core.logger import get_logger

log = get_logger(__name__)


class AgentManager:
    """
    A resilient manager for executing agent functions.
    It provides retry and timeout capabilities.
    """

    def __init__(self, default_timeout: int = 120, default_retries: int = 3):
        """
        Initializes the AgentManager.

        :param default_timeout: Default timeout for agent execution in seconds.
        :param default_retries: Default number of retry attempts.
        """
        self.default_timeout = default_timeout
        self.default_retries = default_retries

    async def execute_agent(
        self,
        agent_func: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Executes an agent function with configured resilience patterns.

        This method wraps the agent execution with a timeout and a retry mechanism.
        The retry mechanism is configured with exponential backoff.

        :param agent_func: The asynchronous agent function to execute.
        :param args: Positional arguments to pass to the agent function.
        :param kwargs: Keyword arguments to pass to the agent function.
        :return: The result from the agent function.
        :raises: `asyncio.TimeoutError` if the agent exceeds the timeout.
                 `tenacity.RetryError` if the agent fails after all retry attempts.
                 Any other exception raised by the agent function.
        """

        # Define the retry decorator dynamically based on instance config
        retry_decorator = retry(
            stop=stop_after_attempt(self.default_retries),
            wait=wait_exponential(multiplier=1, min=2, max=30),
            before_sleep=before_sleep_log(log, "INFO"),
            reraise=True,  # Reraise the last exception after retries are exhausted
        )

        # Wrap the core agent call with the retry logic
        @retry_decorator
        async def resilient_call():
            agent_name = agent_func.__name__
            try:
                log.info(f"Attempting to execute agent: {agent_name}...")
                # The actual execution is wrapped in asyncio.wait_for for the timeout
                result = await asyncio.wait_for(
                    agent_func(*args, **kwargs), timeout=self.default_timeout
                )
                log.info(f"Agent {agent_name} executed successfully.")
                return result
            except asyncio.TimeoutError:
                log.error(
                    f"Agent {agent_name} timed out after {self.default_timeout} seconds."
                )
                # This exception will be caught by the retry decorator
                raise
            except Exception as e:
                log.error(
                    f"Exception during agent execution '{agent_name}': {e}",
                    exc_info=True,
                )
                # This will also be caught by the retry decorator
                raise

        # Execute the wrapped, resilient call
        return await resilient_call()
