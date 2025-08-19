import redis
from backend.core.logger import get_logger
from backend.core.settings import settings

log = get_logger(__name__)

try:
    # Create a Redis connection pool for efficiency
    redis_pool = redis.ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,  # Decode responses from bytes to strings
    )
    """
Redis client setup with graceful fallback.
"""

import redis
from backend.core.settings import Settings
from backend.core.logger import get_logger

settings = Settings()
logger = get_logger(__name__)

# Global Redis instance
r = None

try:
    # Initialize Redis connection
    r = redis.Redis(
        host=settings.REDIS_HOST or 'localhost',
        port=settings.REDIS_PORT or 6379,
        decode_responses=True,
    )
    
    # Test connection
    r.ping()
    logger.info("Redis connection established successfully")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Running without Redis.")
    r = None

def get_redis():
    """Get Redis client instance."""
    return r
except redis.exceptions.ConnectionError as e:
    log.error(
        f"Could not connect to Redis: {e}. Caching will be disabled.", exc_info=True
    )
    redis_pool = None


def get_redis():
    """Gets a Redis connection from the connection pool. Returns None if pool is not available."""
    if redis_pool:
        return redis.Redis(connection_pool=redis_pool)
    return None
