from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestApiSettings(BaseModel):
    base_url: str
    asgi_base_url: str


class TestElasticsearchSettings(BaseModel):
    url: str
    movies_index: str
    genres_index: str
    persons_index: str


class TestRedisSettings(BaseModel):
    url: str


class TestWaitSettings(BaseModel):
    timeout: float
    interval: float


class TestDataSettings(BaseModel):
    path: Path = Path(__file__).resolve().parent / "functional" / "testdata"


class FunctionalTestSettings(BaseSettings):
    """Settings used by functional tests."""

    model_config = SettingsConfigDict(
        env_file=(".env.example", ".env", ".env.test"),
        env_prefix="TEST_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    api: TestApiSettings
    elasticsearch: TestElasticsearchSettings
    redis: TestRedisSettings
    wait: TestWaitSettings
    testdata: TestDataSettings = Field(default_factory=TestDataSettings)


test_settings = FunctionalTestSettings()
