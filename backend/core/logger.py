import logging
import sys

from backend.core.settings import settings
from pythonjsonlogger import jsonlogger

# 1. Get the root logger
logger = logging.getLogger()

# 2. Set the logging level from settings
log_level = logging.DEBUG if settings.DEBUG else logging.INFO
logger.setLevel(log_level)

# 3. Create a handler to write to stdout
logHandler = logging.StreamHandler(sys.stdout)

# 4. Create a specific JSON formatter
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(name)s %(process)d %(thread)d %(levelname)s %(message)s"
)

# 5. Set the formatter for the handler
logHandler.setFormatter(formatter)

# 6. Add the handler to the logger
#    Remove any existing handlers to avoid duplicate logs in some environments
if logger.hasHandlers():
    logger.handlers.clear()
logger.addHandler(logHandler)


def get_logger(name: str) -> logging.Logger:
    """
    A convenience function to get a child logger of the root logger.
    This is best practice for application logging.

    Example:
        from backend.core.logger import get_logger
        log = get_logger(__name__)
        log.info("This is a test log from my module.")
    """
    return logging.getLogger(name)
