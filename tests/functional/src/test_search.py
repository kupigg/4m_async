import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.src.assertions import assert_status
from tests.settings import FunctionalTestSettings

pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest.mark.parametrize(
    "query_string",
    [
        "",
        "?query=",
        "?query=matrix&page_size=0",
        "?query=matrix&page_size=101",
        "?query=matrix&page_number=0",
    ],
)
async def test_search_validation_errors(http_session: aiohttp.ClientSession, query_string: str) -> None:
    await assert_status(http_session, f"/api/v1/films/search/{query_string}", 422)


async def test_search_returns_only_requested_number_of_records(http_session: aiohttp.ClientSession) -> None:
    payload = await assert_status(http_session, "/api/v1/films/search/?query=the&page_size=1", 200)

    assert len(payload) == 1


async def test_search_finds_records_by_phrase(http_session: aiohttp.ClientSession) -> None:
    payload = await assert_status(http_session, "/api/v1/films/search/?query=simulated%20reality", 200)

    assert [item["title"] for item in payload] == ["The Matrix"]


async def test_search_uses_redis_cache(
    http_session: aiohttp.ClientSession,
    es_client: AsyncElasticsearch,
    redis_client,
    settings: FunctionalTestSettings,
) -> None:
    path = "/api/v1/films/search/?query=matrix&page_size=1"

    first_payload = await assert_status(http_session, path, 200)
    assert first_payload[0]["title"] == "The Matrix"
    assert await redis_client.dbsize() > 0

    await es_client.options(ignore_status=[404]).indices.delete(index=settings.elasticsearch.movies_index)

    cached_payload = await assert_status(http_session, path, 200)
    assert cached_payload == first_payload
