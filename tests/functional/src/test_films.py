import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.src.assertions import assert_status
from tests.settings import FunctionalTestSettings

pytestmark = pytest.mark.asyncio

FILM_ID = "aaaaaaaa-1111-1111-1111-aaaaaaaaaaaa"


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/films?page_size=0",
        "/api/v1/films?page_size=101",
        "/api/v1/films?page_number=0",
        "/api/v1/films?sort=-title",
        "/api/v1/films?genre=not-a-uuid",
        "/api/v1/films/not-a-uuid/",
    ],
)
async def test_films_validation_errors(http_session: aiohttp.ClientSession, path: str) -> None:
    await assert_status(http_session, path, 422)


async def test_get_concrete_film(http_session: aiohttp.ClientSession) -> None:
    payload = await assert_status(http_session, f"/api/v1/films/{FILM_ID}/", 200)

    assert payload["uuid"] == FILM_ID
    assert payload["title"] == "The Matrix"
    assert payload["genre"][0]["name"] == "Action"


async def test_list_all_films(http_session: aiohttp.ClientSession) -> None:
    payload = await assert_status(http_session, "/api/v1/films?page_size=10", 200)

    assert {item["title"] for item in payload} == {"The Matrix", "John Wick", "Quiet Drama"}


async def test_films_use_redis_cache(
    http_session: aiohttp.ClientSession,
    es_client: AsyncElasticsearch,
    redis_client,
    settings: FunctionalTestSettings,
) -> None:
    path = f"/api/v1/films/{FILM_ID}/"

    first_payload = await assert_status(http_session, path, 200)
    assert await redis_client.dbsize() > 0

    await es_client.options(ignore_status=[404]).indices.delete(index=settings.elasticsearch.movies_index)

    cached_payload = await assert_status(http_session, path, 200)
    assert cached_payload == first_payload
