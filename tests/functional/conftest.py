import asyncio
from collections.abc import AsyncIterator

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from tests.functional.utils.es_loader import load_test_data
from tests.functional.utils.wait_for_services import wait_for_services
from tests.settings import FunctionalTestSettings


@pytest_asyncio.fixture(scope="session")
def event_loop() -> AsyncIterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def wait_for_test_services(settings: FunctionalTestSettings) -> None:
    wait_for_services(settings)


@pytest_asyncio.fixture(scope="session")
async def http_session(settings: FunctionalTestSettings) -> AsyncIterator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession(base_url=settings.api.base_url) as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def es_client(settings: FunctionalTestSettings) -> AsyncIterator[AsyncElasticsearch]:
    client = AsyncElasticsearch(hosts=settings.elasticsearch.url)
    try:
        yield client
    finally:
        await client.close()


@pytest_asyncio.fixture(scope="session")
async def redis_client(settings: FunctionalTestSettings) -> AsyncIterator[Redis]:
    client = Redis.from_url(settings.redis.url, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture(autouse=True)
async def prepare_data(
    settings: FunctionalTestSettings,
    es_client: AsyncElasticsearch,
    redis_client: Redis,
) -> None:
    await redis_client.flushdb()
    await load_test_data(es_client, settings)
