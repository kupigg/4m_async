from functools import lru_cache

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseModel):
    project_name: str = "cinema-api"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

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


class ElasticsearchSettings(BaseModel):
    scheme: str = "http"
    host: str = "elasticsearch"
    port: int = 9200
    request_timeout: int = 5
    connections_per_node: int = 50
    max_retries: int = 2
    retry_on_timeout: bool = True
    movies_index: str = "movies"
    genres_index: str = "genres"
    persons_index: str = "persons"
    user: str | None = None
    password: str | None = None

    @property
    def url(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"


class RedisSettings(BaseModel):
    host: str = "redis"
    port: int = 6379
    password: str | None = None
    socket_timeout: float = 5.0
    decode_responses: bool = True
    max_connections: int = 1000


class UvicornSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    workers: int = 4
    backlog: int = 4096
    limit_concurrency: int = 10000
    timeout_keep_alive: int = 5


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app: AppSettings = Field(default_factory=AppSettings)
    elasticsearch: ElasticsearchSettings = Field(default_factory=ElasticsearchSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    uvicorn: UvicornSettings = Field(default_factory=UvicornSettings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
