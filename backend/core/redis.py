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
    # Test connection
    r = redis.Redis(connection_pool=redis_pool)
    r.ping()
    log.info("Redis connection pool created successfully.")
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
