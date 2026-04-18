import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.src.assertions import assert_status
from tests.settings import FunctionalTestSettings

pytestmark = pytest.mark.asyncio(loop_scope="session")

GENRE_ID = "11111111-1111-1111-1111-111111111111"


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/genres/?page_size=0",
        "/api/v1/genres/?page_size=101",
        "/api/v1/genres/?page_number=0",
        "/api/v1/genres/not-a-uuid/",
    ],
)
async def test_genres_validation_errors(http_session: aiohttp.ClientSession, path: str) -> None:
    await assert_status(http_session, path, 422)


async def test_get_concrete_genre(http_session: aiohttp.ClientSession) -> None:
    payload = await assert_status(http_session, f"/api/v1/genres/{GENRE_ID}/", 200)

    assert payload["uuid"] == GENRE_ID
    assert payload["name"] == "Action"


async def test_list_all_genres(http_session: aiohttp.ClientSession) -> None:
    payload = await assert_status(http_session, "/api/v1/genres/?page_size=10", 200)

    assert [item["name"] for item in payload] == ["Action", "Drama"]


async def test_genres_use_redis_cache(
    http_session: aiohttp.ClientSession,
    es_client: AsyncElasticsearch,
    redis_client,
    settings: FunctionalTestSettings,
) -> None:
    path = f"/api/v1/genres/{GENRE_ID}/"

    first_payload = await assert_status(http_session, path, 200)
    assert await redis_client.dbsize() > 0

    await es_client.options(ignore_status=[404]).indices.delete(index=settings.elasticsearch.genres_index)

    cached_payload = await assert_status(http_session, path, 200)
    assert cached_payload == first_payload
