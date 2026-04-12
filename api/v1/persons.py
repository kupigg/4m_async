from uuid import UUID

from fastapi import APIRouter, Query

from core.settings import get_settings
from schemas.film import FilmListItem
from schemas.person import PersonDetailItem, PersonSearchItem
from utils.es import first_hit_or_404, search_or_503
from utils.films import build_films_by_person_query, parse_film_hits
from utils.persons import (
    build_person_by_id_query,
    build_persons_search_query,
    parse_person_detail,
    parse_person_search_hits,
)

router = APIRouter(prefix="/persons")


@router.get("/search/", response_model=list[PersonSearchItem], summary="Search Persons")
async def search_persons(
    query: str = Query(min_length=1),
    page_size: int = Query(default=50, ge=1, le=100),
    page_number: int = Query(default=1, ge=1),
) -> list[PersonSearchItem]:
    settings = get_settings()
    body = build_persons_search_query(query=query, page_size=page_size, page_number=page_number)
    response = await search_or_503(settings.es_persons_index, body, "Persons")
    return parse_person_search_hits(response.get("hits", {}).get("hits", []))


@router.get("/{person_id}/", response_model=PersonDetailItem, summary="Get Person Details")
async def get_person(person_id: UUID) -> PersonDetailItem:
    settings = get_settings()
    response = await search_or_503(settings.es_persons_index, build_person_by_id_query(person_id), "Persons")
    hit = first_hit_or_404(response, "Person not found")
    return parse_person_detail(hit.get("_source", {}))


@router.get("/{person_id}/film/", response_model=list[FilmListItem], summary="List Films By Person")
async def list_person_films(
    person_id: UUID,
    page_size: int = Query(default=50, ge=1, le=100),
    page_number: int = Query(default=1, ge=1),
) -> list[FilmListItem]:
    settings = get_settings()
    body = build_films_by_person_query(person_id=person_id, page_size=page_size, page_number=page_number)
    response = await search_or_503(settings.es_movies_index, body, "Movies")
    return parse_film_hits(response.get("hits", {}).get("hits", []))
