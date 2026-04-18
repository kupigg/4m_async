from collections.abc import AsyncIterator

import aiohttp
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from tests.functional.utils.es_loader import load_test_data
from tests.functional.utils.wait_for_services import wait_for_services
from tests.settings import FunctionalTestSettings


@pytest.fixture(scope="session", autouse=True)
def wait_for_test_services(settings: FunctionalTestSettings) -> None:
    wait_for_services(settings)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def http_session(
    settings: FunctionalTestSettings,
    wait_for_test_services: None,
) -> AsyncIterator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession(base_url=settings.api.base_url) as session:
        yield session


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def es_client(
    settings: FunctionalTestSettings,
    wait_for_test_services: None,
) -> AsyncIterator[AsyncElasticsearch]:
    client = AsyncElasticsearch(hosts=settings.elasticsearch.url)
    try:
        yield client
    finally:
        await client.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def redis_client(
    settings: FunctionalTestSettings,
    wait_for_test_services: None,
) -> AsyncIterator[Redis]:
    client = Redis.from_url(settings.redis.url, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def prepare_data(
    settings: FunctionalTestSettings,
    es_client: AsyncElasticsearch,
    redis_client: Redis,
) -> None:
    await redis_client.flushdb()
    await load_test_data(es_client, settings)
