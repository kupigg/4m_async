from uuid import UUID

from schemas.film import FilmDetailItem, FilmGenreItem, FilmListItem, FilmPersonItem

ALLOWED_FILM_SORTS = {"imdb_rating", "-imdb_rating"}


def resolve_film_sort(sort: str) -> tuple[str, str]:
    if sort not in ALLOWED_FILM_SORTS:
        raise ValueError("Only imdb_rating sort is supported")

    sort_field = sort.removeprefix("-")
    sort_order = "desc" if sort.startswith("-") else "asc"
    return sort_field, sort_order


def build_films_query(
    sort_field: str,
    sort_order: str,
    page_size: int,
    page_number: int,
    genre: UUID | None,
) -> dict:
    query: dict = {"match_all": {}}
    if genre is not None:
        query = {
            "bool": {
                "filter": [
                    {"term": {"genres.id": str(genre)}},
                ]
            }
        }

    return {
        "query": query,
        "from": (page_number - 1) * page_size,
        "size": page_size,
        "sort": [{sort_field: {"order": sort_order, "missing": "_last"}}],
    }


def build_films_search_query(query: str, page_size: int, page_number: int) -> dict:
    return {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "description"],
                "fuzziness": "auto",
            }
        },
        "from": (page_number - 1) * page_size,
        "size": page_size,
        "sort": [{"imdb_rating": {"order": "desc", "missing": "_last"}}],
    }


def build_film_by_id_query(film_id: UUID) -> dict:
    return {
        "query": {"term": {"id": str(film_id)}},
        "size": 1,
    }


def build_films_by_person_query(person_id: UUID, page_size: int, page_number: int) -> dict:
    return {
        "query": {
            "term": {"persons.id": str(person_id)},
        },
        "from": (page_number - 1) * page_size,
        "size": page_size,
        "sort": [{"imdb_rating": {"order": "desc", "missing": "_last"}}],
    }


def _to_rating(raw_rating: object) -> float | None:
    if raw_rating is None:
        return None
    try:
        return float(raw_rating)
    except (TypeError, ValueError):
        return None


def parse_film_hits(hits: list[dict]) -> list[FilmListItem]:
    items: list[FilmListItem] = []
    for hit in hits:
        source = hit.get("_source", {})
        items.append(
            FilmListItem(
                uuid=str(source["id"]),
                title=str(source.get("title", "")),
                imdb_rating=_to_rating(source.get("imdb_rating")),
            )
        )

    return items


def parse_film_detail(source: dict) -> FilmDetailItem:
    return FilmDetailItem(
        uuid=str(source["id"]),
        title=str(source.get("title", "")),
        imdb_rating=_to_rating(source.get("imdb_rating")),
        description=source.get("description"),
        genre=[
            FilmGenreItem(uuid=str(item["id"]), name=str(item.get("name", "")))
            for item in source.get("genres", [])
        ],
        actors=[
            FilmPersonItem(uuid=str(item["id"]), full_name=str(item.get("full_name", "")))
            for item in source.get("actors", [])
        ],
        writers=[
            FilmPersonItem(uuid=str(item["id"]), full_name=str(item.get("full_name", "")))
            for item in source.get("writers", [])
        ],
        directors=[
            FilmPersonItem(uuid=str(item["id"]), full_name=str(item.get("full_name", "")))
            for item in source.get("directors", [])
        ],
    )
