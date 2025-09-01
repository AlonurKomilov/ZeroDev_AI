# Backend Performance Optimizations

## 1. Database Performance Enhancements

### Database Connection Pooling
```python
# backend/core/database.py - Enhanced version
from sqlalchemy.pool import QueuePool
from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = settings.DATABASE_URL

# Enhanced engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections when pool is full
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "options": "-c timezone=utc",
        "application_name": "zerodev_backend",
    }
)

# Add async session support
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async_engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
)

async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

### Database Query Optimizations
```python
# backend/services/optimized_queries.py
from sqlmodel import select
from sqlalchemy.orm import selectinload, joinedload

class OptimizedProjectService:
    @staticmethod
    async def get_projects_with_stats(user_id: str, session: AsyncSession):
        # Optimized query with eager loading
        stmt = (
            select(Project)
            .where(Project.user_id == user_id)
            .options(
                selectinload(Project.analytics),
                joinedload(Project.templates)
            )
            .order_by(Project.updated_at.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_project_counts_by_user():
        # Bulk aggregation query
        stmt = """
        SELECT 
            user_id,
            COUNT(*) as total_projects,
            COUNT(CASE WHEN status = 'active' THEN 1 END) as active_projects,
            MAX(updated_at) as last_activity
        FROM projects 
        GROUP BY user_id
        """
        return await session.execute(text(stmt))

# Add database indexes
# migrations/versions/add_performance_indexes.py
def upgrade():
    op.create_index('idx_projects_user_status', 'projects', ['user_id', 'status'])
    op.create_index('idx_projects_updated_at', 'projects', ['updated_at'])
    op.create_index('idx_analytics_created_at', 'analytics', ['created_at'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
```

## 2. Redis Performance Enhancements

### Advanced Caching Strategies
```python
# backend/core/advanced_cache.py
import asyncio
from typing import Optional, Union, List
from redis.asyncio import Redis
from redis.commands.json.path import Path as JSONPath

class AdvancedCache:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.pipe = self.redis.pipeline()
    
    async def multi_get(self, keys: List[str]) -> dict:
        """Batch get multiple keys efficiently"""
        values = await self.redis.mget(keys)
        return {k: json.loads(v) if v else None for k, v in zip(keys, values)}
    
    async def set_with_tags(self, key: str, value: dict, ttl: int, tags: List[str]):
        """Set cache with tags for bulk invalidation"""
        pipe = self.redis.pipeline()
        pipe.setex(key, ttl, json.dumps(value))
        for tag in tags:
            pipe.sadd(f"tag:{tag}", key)
            pipe.expire(f"tag:{tag}", ttl + 3600)  # Keep tags longer
        await pipe.execute()
    
    async def invalidate_by_tag(self, tag: str):
        """Invalidate all keys with specific tag"""
        keys = await self.redis.smembers(f"tag:{tag}")
        if keys:
            pipe = self.redis.pipeline()
            pipe.delete(*keys)
            pipe.delete(f"tag:{tag}")
            await pipe.execute()
    
    async def cache_with_refresh(self, key: str, factory_func, ttl: int):
        """Cache with background refresh"""
        value = await self.redis.get(key)
        if value:
            # Check if close to expiry (refresh in background)
            remaining_ttl = await self.redis.ttl(key)
            if remaining_ttl < ttl * 0.2:  # Refresh when 20% TTL remains
                asyncio.create_task(self._background_refresh(key, factory_func, ttl))
            return json.loads(value)
        
        # Cache miss - get value and cache
        fresh_value = await factory_func()
        await self.redis.setex(key, ttl, json.dumps(fresh_value))
        return fresh_value

# Cache warming strategies
async def warm_cache():
    """Pre-populate frequently accessed data"""
    cache = AdvancedCache(settings.REDIS_URL)
    
    # Warm user project counts
    users = await get_active_users()
    for user in users:
        cache_key = f"user:{user.id}:project_count"
        count = await get_project_count(user.id)
        await cache.redis.setex(cache_key, 3600, count)
    
    # Warm template data
    templates = await get_popular_templates()
    await cache.redis.setex("templates:popular", 1800, json.dumps(templates))
```

## 3. Celery Performance Optimizations

### Enhanced Celery Configuration
```python
# backend/core/celery_app.py - Enhanced version
from kombu import Queue

celery_app.conf.update(
    # Performance settings
    worker_concurrency=4,  # Adjust based on CPU cores
    worker_prefetch_multiplier=1,  # Don't prefetch tasks
    task_acks_late=True,  # Acknowledge after completion
    worker_max_tasks_per_child=1000,  # Restart workers periodically
    
    # Queue configuration
    task_routes={
        'tasks.heavy_computation': {'queue': 'heavy'},
        'tasks.quick_tasks': {'queue': 'quick'},
        'tasks.ai_generation': {'queue': 'ai'},
    },
    
    task_default_queue='default',
    task_queues=(
        Queue('default', routing_key='default'),
        Queue('quick', routing_key='quick'),
        Queue('heavy', routing_key='heavy'),
        Queue('ai', routing_key='ai'),
    ),
    
    # Result backend optimization
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        'master_name': 'mymaster',
    },
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Task priorities and routing
@celery_app.task(bind=True, priority=5)  # High priority
def urgent_ai_task(self, prompt: str):
    pass

@celery_app.task(bind=True, priority=1)  # Low priority
def background_cleanup_task(self):
    pass
```

### Task Result Caching
```python
# backend/core/task_cache.py
from functools import wraps
from celery import current_task

def cache_task_result(ttl: int = 3600):
    """Cache Celery task results to avoid recomputation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from task name and args
            task_id = current_task.request.id if current_task else None
            cache_key = f"task_result:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            redis_client = get_redis()
            if redis_client:
                cached = redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            
            result = func(*args, **kwargs)
            
            if redis_client:
                redis_client.setex(cache_key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Usage
@celery_app.task
@cache_task_result(ttl=1800)
def expensive_ai_analysis(code_content: str):
    # Expensive AI analysis that can be cached
    pass
```

## 4. API Response Optimization

### Response Compression and Caching
```python
# backend/core/middleware.py - Enhanced version
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Enhanced caching middleware
class ResponseCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip caching for non-GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Skip caching for authenticated endpoints
        if "authorization" in request.headers:
            return await call_next(request)
        
        cache_key = f"response:{request.url.path}:{request.url.query}"
        redis_client = get_redis()
        
        if redis_client:
            cached_response = await redis_client.get(cache_key)
            if cached_response:
                data = json.loads(cached_response)
                return Response(
                    content=data["content"],
                    status_code=data["status_code"],
                    headers=data["headers"],
                    media_type=data["media_type"]
                )
        
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200 and redis_client:
            response_data = {
                "content": response.body.decode(),
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "media_type": response.media_type
            }
            await redis_client.setex(cache_key, 300, json.dumps(response_data))
        
        return response

app.add_middleware(ResponseCacheMiddleware)
```

### Pagination and Filtering
```python
# backend/core/pagination.py
from sqlalchemy import func, select
from sqlmodel import Session

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = "created_at"
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

async def paginate_query(
    session: Session,
    query: select,
    pagination: PaginationParams
) -> PaginatedResponse:
    # Get total count
    count_query = select(func.count()).select_from(query.alias())
    total = (await session.execute(count_query)).scalar()
    
    # Apply sorting
    if hasattr(query.column_descriptions[0]["entity"], pagination.sort_by):
        sort_column = getattr(query.column_descriptions[0]["entity"], pagination.sort_by)
        if pagination.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.size
    query = query.offset(offset).limit(pagination.size)
    
    # Execute query
    result = await session.execute(query)
    items = result.scalars().all()
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=math.ceil(total / pagination.size)
    )
```

## 5. AI Model Performance

### Model Response Caching
```python
# backend/core/ai_cache.py
class AIModelCache:
    def __init__(self):
        self.redis = get_redis()
        self.ttl = 86400  # 24 hours
    
    def _generate_key(self, model: str, prompt: str, params: dict) -> str:
        """Generate cache key from model and prompt"""
        param_str = json.dumps(params, sort_keys=True)
        content = f"{model}:{prompt}:{param_str}"
        return f"ai_cache:{hashlib.sha256(content.encode()).hexdigest()}"
    
    async def get_cached_response(self, model: str, prompt: str, params: dict):
        """Get cached AI response"""
        if not self.redis:
            return None
        
        cache_key = self._generate_key(model, prompt, params)
        cached = await self.redis.get(cache_key)
        
        if cached:
            return json.loads(cached)
        return None
    
    async def cache_response(self, model: str, prompt: str, params: dict, response: dict):
        """Cache AI response"""
        if not self.redis:
            return
        
        cache_key = self._generate_key(model, prompt, params)
        await self.redis.setex(cache_key, self.ttl, json.dumps(response))
        
        # Track cache usage
        await self.redis.incr("ai_cache:hits")

# Enhanced AI Router with caching
class CachedAIRouter:
    def __init__(self):
        self.cache = AIModelCache()
        self.rate_limiter = AsyncLimiter(max_rate=100, time_period=60)  # 100 req/min
    
    async def chat_completion(self, model: str, messages: list, **kwargs):
        # Check rate limit
        async with self.rate_limiter:
            # Try cache first
            prompt_key = json.dumps(messages, sort_keys=True)
            cached = await self.cache.get_cached_response(model, prompt_key, kwargs)
            
            if cached:
                await self.redis.incr("ai_cache:hits")
                return cached
            
            # Make API call
            adapter = get_llm_adapter(model)
            response = await adapter.chat_completion(messages, **kwargs)
            
            # Cache response
            await self.cache.cache_response(model, prompt_key, kwargs, response)
            await self.redis.incr("ai_cache:misses")
            
            return response
```

## 6. Monitoring and Observability

### Performance Metrics Collection
```python
# backend/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_db_connections', 'Active database connections')
CELERY_TASK_DURATION = Histogram('celery_task_duration_seconds', 'Celery task duration', ['task_name'])
AI_MODEL_USAGE = Counter('ai_model_requests_total', 'AI model requests', ['model', 'status'])

# Middleware for metrics collection
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        REQUEST_DURATION.observe(duration)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        return response

# Database connection monitoring
async def monitor_db_connections():
    while True:
        active_connections = await get_active_connection_count()
        ACTIVE_CONNECTIONS.set(active_connections)
        await asyncio.sleep(10)

# Task monitoring decorator
def monitor_task_performance(task_func):
    @wraps(task_func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = task_func(*args, **kwargs)
            CELERY_TASK_DURATION.labels(task_name=task_func.__name__).observe(
                time.time() - start_time
            )
            return result
        except Exception as e:
            CELERY_TASK_DURATION.labels(task_name=f"{task_func.__name__}_error").observe(
                time.time() - start_time
            )
            raise
    return wrapper
```
