from uuid import UUID

from schemas.person import PersonDetailItem, PersonFilmItem, PersonSearchItem


def build_persons_search_query(query: str, page_size: int, page_number: int) -> dict:
    return {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["full_name^2", "name", "description"],
                "fuzziness": "auto",
            }
        },
        "from": (page_number - 1) * page_size,
        "size": page_size,
    }


def build_person_by_id_query(person_id: UUID) -> dict:
    return {
        "query": {"term": {"id": str(person_id)}},
        "size": 1,
    }


def parse_person_films(source: dict) -> list[PersonFilmItem]:
    return [
        PersonFilmItem(uuid=str(item["id"]), roles=[str(role) for role in item.get("roles", [])])
        for item in source.get("films", [])
    ]


def parse_person_search_hits(hits: list[dict]) -> list[PersonSearchItem]:
    items: list[PersonSearchItem] = []
    for hit in hits:
        source = hit.get("_source", {})
        items.append(
            PersonSearchItem(
                uuid=str(source["id"]),
                full_name=str(source.get("full_name") or source.get("name") or ""),
                films=parse_person_films(source),
            )
        )
    return items


def parse_person_detail(source: dict) -> PersonDetailItem:
    return PersonDetailItem(
        uuid=str(source["id"]),
        full_name=str(source.get("full_name") or source.get("name") or ""),
        films=parse_person_films(source),
    )
