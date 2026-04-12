from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from core.settings import get_settings
from schemas.film import FilmDetailItem, FilmListItem
from utils.es import first_hit_or_404, search_or_503
from utils.films import (
    build_film_by_id_query,
    build_films_query,
    build_films_search_query,
    parse_film_detail,
    parse_film_hits,
    resolve_film_sort,
)

router = APIRouter(prefix="/films")


@router.get("", response_model=list[FilmListItem], summary="List Popular Films")
async def list_films(
    sort: str = Query(default="-imdb_rating"),
    page_size: int = Query(default=50, ge=1, le=100),
    page_number: int = Query(default=1, ge=1),
    genre: UUID | None = Query(default=None),
) -> list[FilmListItem]:
    settings = get_settings()

    try:
        sort_field, sort_order = resolve_film_sort(sort)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    body = build_films_query(
        sort_field=sort_field,
        sort_order=sort_order,
        page_size=page_size,
        page_number=page_number,
        genre=genre,
    )
    response = await search_or_503(settings.elasticsearch.movies_index, body, "Movies")
    return parse_film_hits(response.get("hits", {}).get("hits", []))


@router.get("/search/", response_model=list[FilmListItem], summary="Search Films")
async def search_films(
    query: str = Query(min_length=1),
    page_size: int = Query(default=50, ge=1, le=100),
    page_number: int = Query(default=1, ge=1),
) -> list[FilmListItem]:
    settings = get_settings()
    body = build_films_search_query(query=query, page_size=page_size, page_number=page_number)
    response = await search_or_503(settings.elasticsearch.movies_index, body, "Movies")
    return parse_film_hits(response.get("hits", {}).get("hits", []))


@router.get("/{film_id}/", response_model=FilmDetailItem, summary="Get Film Details")
async def get_film(film_id: UUID) -> FilmDetailItem:
    settings = get_settings()
    response = await search_or_503(settings.elasticsearch.movies_index, build_film_by_id_query(film_id), "Movies")
    hit = first_hit_or_404(response, "Film not found")
    return parse_film_detail(hit.get("_source", {}))
