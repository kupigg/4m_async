import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch

from tests.functional.src.assertions import assert_status
from tests.settings import FunctionalTestSettings

pytestmark = pytest.mark.asyncio

PERSON_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/persons?page_size=0",
        "/api/v1/persons?page_size=101",
        "/api/v1/persons?page_number=0",
        "/api/v1/persons/search/",
        "/api/v1/persons/search/?query=",
        "/api/v1/persons/search/?query=keanu&page_size=0",
        "/api/v1/persons/search/?query=keanu&page_size=101",
        "/api/v1/persons/search/?query=keanu&page_number=0",
        "/api/v1/persons/not-a-uuid/",
        "/api/v1/persons/not-a-uuid/film/",
    ],
)
async def test_persons_validation_errors(http_session: aiohttp.ClientSession, path: str) -> None:
    await assert_status(http_session, path, 422)


async def test_get_concrete_person(http_session: aiohttp.ClientSession) -> None:
    payload = await assert_status(http_session, f"/api/v1/persons/{PERSON_ID}/", 200)

    assert payload["uuid"] == PERSON_ID
    assert payload["full_name"] == "Keanu Reeves"


async def test_get_all_person_films(http_session: aiohttp.ClientSession) -> None:
    payload = await assert_status(http_session, f"/api/v1/persons/{PERSON_ID}/film/?page_size=10", 200)

    assert {item["title"] for item in payload} == {"The Matrix", "John Wick"}


async def test_list_all_persons(http_session: aiohttp.ClientSession) -> None:
    payload = await assert_status(http_session, "/api/v1/persons/?page_size=10", 200)

    assert {item["full_name"] for item in payload} == {
        "Carrie Anne Moss",
        "Keanu Reeves",
        "Lana Wachowski",
    }


async def test_person_search_finds_record_by_phrase(http_session: aiohttp.ClientSession) -> None:
    payload = await assert_status(http_session, "/api/v1/persons/search/?query=director", 200)

    assert [item["full_name"] for item in payload] == ["Lana Wachowski"]


async def test_persons_use_redis_cache(
    http_session: aiohttp.ClientSession,
    es_client: AsyncElasticsearch,
    redis_client,
    settings: FunctionalTestSettings,
) -> None:
    path = f"/api/v1/persons/{PERSON_ID}/"

    first_payload = await assert_status(http_session, path, 200)
    assert await redis_client.dbsize() > 0

    await es_client.options(ignore_status=[404]).indices.delete(index=settings.elasticsearch.persons_index)

    cached_payload = await assert_status(http_session, path, 200)
    assert cached_payload == first_payload
