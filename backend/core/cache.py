import functools
import json
from typing import Callable, Any

import redis
from backend.core.redis import get_redis
from backend.core.logger import get_logger

log = get_logger(__name__)


def cache(ttl: int = 3600) -> Callable:
    """
    A decorator to cache function results in Redis.
    The result of the decorated function must be JSON serializable.

    :param ttl: Time-to-live for the cache key in seconds. Defaults to 1 hour.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            redis_conn = get_redis()
            if not redis_conn:
                # If Redis is not available, just call the function directly
                return func(*args, **kwargs)

            # Generate a cache key from the function name and arguments
            key_parts = [func.__module__, func.__name__] + list(map(str, args))
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = "cache:" + ":".join(key_parts)

            try:
                # Check for cached result
                cached_result = redis_conn.get(cache_key)
                if cached_result:
                    log.debug(f"Cache HIT for key: {cache_key}")
                    return json.loads(cached_result)

                # If not cached, call the function
                log.debug(f"Cache MISS for key: {cache_key}")
                result = func(*args, **kwargs)

                # Cache the result, ensuring it's JSON serializable
                try:
                    serialized_result = json.dumps(result)
                    redis_conn.setex(cache_key, ttl, serialized_result)
                except (TypeError, redis.exceptions.RedisError) as e:
                    log.warning(f"Could not cache result for {cache_key}. Reason: {e}")

                return result
            except redis.exceptions.RedisError as e:
                log.error(f"Redis cache error for key {cache_key}: {e}. Falling back to function call.", exc_info=True)
                # In case of Redis error, just call the function without caching
                return func(*args, **kwargs)

        return wrapper
    return decorator
