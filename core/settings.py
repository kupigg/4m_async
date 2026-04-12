from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "cinema-api"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    es_scheme: str = "http"
    es_host: str = "elasticsearch"
    es_port: int = 9200
    es_request_timeout: int = 5
    es_connections_per_node: int = 50
    es_max_retries: int = 2
    es_retry_on_timeout: bool = True
    es_movies_index: str = "movies"
    es_genres_index: str = "genres"
    es_persons_index: str = "persons"
    es_user: str | None = None
    es_password: str | None = None

    redis_startup_nodes: list[str] = Field(
        default_factory=lambda: [
            "redis-cluster:7000",
            "redis-cluster:7001",
            "redis-cluster:7002",
            "redis-cluster:7003",
            "redis-cluster:7004",
            "redis-cluster:7005",
        ]
    )
    redis_password: str | None = None
    redis_socket_timeout: float = 5.0
    redis_decode_responses: bool = True
    redis_max_connections: int = 1000

    uvicorn_host: str = "0.0.0.0"
    uvicorn_port: int = 8000
    uvicorn_reload: bool = False
    uvicorn_workers: int = 4
    uvicorn_backlog: int = 4096
    uvicorn_limit_concurrency: int = 10000
    uvicorn_timeout_keep_alive: int = 5

    @property
    def elasticsearch_url(self) -> str:
        return f"{self.es_scheme}://{self.es_host}:{self.es_port}"

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: bool | str) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "yes", "on", "debug"}:
                return True
            if lowered in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        raise ValueError("debug must be a boolean value")

    @field_validator("redis_startup_nodes", mode="before")
    @classmethod
    def parse_redis_startup_nodes(cls, value: str | list[str]):
        if isinstance(value, str):
            return [node.strip() for node in value.split(",") if node.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
