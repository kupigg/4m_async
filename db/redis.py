from redis.asyncio.cluster import RedisCluster

from core.settings import get_settings


class RedisManager:
    def __init__(self) -> None:
        self._client: RedisCluster | None = None

    async def init(self) -> RedisCluster:
        settings = get_settings()
        startup_nodes: list[dict[str, str | int]] = []
        for node in settings.redis_startup_nodes:
            host, port = node.split(":", maxsplit=1)
            startup_nodes.append({"host": host, "port": int(port)})

        self._client = RedisCluster(
            startup_nodes=startup_nodes,
            password=settings.redis_password,
            socket_timeout=settings.redis_socket_timeout,
            decode_responses=settings.redis_decode_responses,
            max_connections=settings.redis_max_connections,
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
            result = await self._client.ping()
            if isinstance(result, dict):
                return all(value for value in result.values())
            return bool(result)
        except Exception:
            return False

    @property
    def client(self) -> RedisCluster:
        if self._client is None:
            raise RuntimeError("Redis client is not initialized")
        return self._client


redis_manager = RedisManager()
