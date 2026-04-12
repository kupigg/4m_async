from redis.asyncio import Redis

from core.settings import get_settings


class RedisManager:
    def __init__(self) -> None:
        self._client: Redis | None = None

    async def init(self) -> Redis:
        settings = get_settings()
        redis = settings.redis
        self._client = Redis(
            host=redis.host,
            port=redis.port,
            password=redis.password,
            socket_timeout=redis.socket_timeout,
            decode_responses=redis.decode_responses,
            max_connections=redis.max_connections,
        )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def ping(self) -> bool:
        if self._client is None:
            return False
        try:
            return bool(await self._client.ping())
        except Exception:
            return False

    @property
    def client(self) -> Redis:
        if self._client is None:
            raise RuntimeError("Redis client is not initialized")
        return self._client


redis_manager = RedisManager()
