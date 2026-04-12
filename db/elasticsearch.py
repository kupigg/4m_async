from elasticsearch import AsyncElasticsearch

from core.settings import get_settings


class ElasticsearchManager:
    def __init__(self) -> None:
        self._client: AsyncElasticsearch | None = None

    async def init(self) -> AsyncElasticsearch:
        settings = get_settings()
        kwargs = {
            "hosts": [settings.elasticsearch_url],
            "request_timeout": settings.es_request_timeout,
            "connections_per_node": settings.es_connections_per_node,
            "max_retries": settings.es_max_retries,
            "retry_on_timeout": settings.es_retry_on_timeout,
        }
        if settings.es_user and settings.es_password:
            kwargs["basic_auth"] = (settings.es_user, settings.es_password)
        self._client = AsyncElasticsearch(**kwargs)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def ping(self) -> bool:
        if self._client is None:
            return False
        try:
            return bool(await self._client.ping())
        except Exception:
            return False

    @property
    def client(self) -> AsyncElasticsearch:
        if self._client is None:
            raise RuntimeError("Elasticsearch client is not initialized")
        return self._client


es_manager = ElasticsearchManager()
