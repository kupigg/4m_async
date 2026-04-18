import json
from pathlib import Path

from elasticsearch import AsyncElasticsearch

from tests.settings import FunctionalTestSettings


MOVIES_MAPPING = {
    "properties": {
        "id": {"type": "keyword"},
        "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "description": {"type": "text"},
        "imdb_rating": {"type": "float"},
        "genres": {
            "properties": {
                "id": {"type": "keyword"},
                "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            }
        },
        "persons": {
            "properties": {
                "id": {"type": "keyword"},
                "full_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            }
        },
    }
}

PERSONS_MAPPING = {
    "properties": {
        "id": {"type": "keyword"},
        "full_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "description": {"type": "text"},
        "films": {
            "properties": {
                "id": {"type": "keyword"},
                "roles": {"type": "keyword"},
            }
        },
    }
}

GENRES_MAPPING = {
    "properties": {
        "id": {"type": "keyword"},
        "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
        "description": {"type": "text"},
    }
}


def load_json(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


async def recreate_index(
    es_client: AsyncElasticsearch,
    index: str,
    mapping: dict,
    documents: list[dict],
) -> None:
    await es_client.options(ignore_status=[404]).indices.delete(index=index)
    await es_client.indices.create(index=index, mappings=mapping)

    operations: list[dict] = []
    for document in documents:
        operations.append({"index": {"_index": index, "_id": document["id"]}})
        operations.append(document)

    if operations:
        response = await es_client.bulk(operations=operations, refresh=True)
        if response.get("errors"):
            raise RuntimeError(f"Failed to load test data into {index}: {response}")


async def load_test_data(es_client: AsyncElasticsearch, settings: FunctionalTestSettings) -> None:
    await recreate_index(
        es_client,
        settings.elasticsearch.movies_index,
        MOVIES_MAPPING,
        load_json(settings.testdata.path / "movies.json"),
    )
    await recreate_index(
        es_client,
        settings.elasticsearch.persons_index,
        PERSONS_MAPPING,
        load_json(settings.testdata.path / "persons.json"),
    )
    await recreate_index(
        es_client,
        settings.elasticsearch.genres_index,
        GENRES_MAPPING,
        load_json(settings.testdata.path / "genres.json"),
    )
