from uuid import UUID

from schemas.genre import GenreDetailItem, GenreListItem


def build_genres_query(page_size: int, page_number: int) -> dict:
    return {
        "query": {"match_all": {}},
        "from": (page_number - 1) * page_size,
        "size": page_size,
        "sort": [{"name": {"order": "asc", "missing": "_last"}}],
    }


def build_genre_by_id_query(genre_id: UUID) -> dict:
    return {
        "query": {"term": {"id": str(genre_id)}},
        "size": 1,
    }


def parse_genre_hits(hits: list[dict]) -> list[GenreListItem]:
    items: list[GenreListItem] = []
    for hit in hits:
        source = hit.get("_source", {})
        items.append(
            GenreListItem(
                uuid=str(source["id"]),
                name=str(source.get("name") or source.get("title") or ""),
                description=source.get("description"),
            )
        )
    return items


def parse_genre_detail(source: dict) -> GenreDetailItem:
    return GenreDetailItem(
        uuid=str(source["id"]),
        name=str(source.get("name") or source.get("title") or ""),
        description=source.get("description"),
    )
