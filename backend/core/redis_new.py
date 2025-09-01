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
