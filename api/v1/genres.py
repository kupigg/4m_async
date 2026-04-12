from uuid import UUID

from fastapi import APIRouter, Query

from core.settings import get_settings
from schemas.genre import GenreDetailItem, GenreListItem
from utils.es import first_hit_or_404, search_or_503
from utils.genres import build_genre_by_id_query, build_genres_query, parse_genre_detail, parse_genre_hits

router = APIRouter(prefix="/genres")


@router.get("/", response_model=list[GenreListItem], summary="List Genres")
async def list_genres(
    page_size: int = Query(default=50, ge=1, le=100),
    page_number: int = Query(default=1, ge=1),
) -> list[GenreListItem]:
    settings = get_settings()
    response = await search_or_503(
        settings.elasticsearch.genres_index,
        build_genres_query(page_size=page_size, page_number=page_number),
        "Genres",
    )
    return parse_genre_hits(response.get("hits", {}).get("hits", []))


@router.get("/{genre_id}/", response_model=GenreDetailItem, summary="Get Genre Details")
async def get_genre(genre_id: UUID) -> GenreDetailItem:
    settings = get_settings()
    response = await search_or_503(settings.elasticsearch.genres_index, build_genre_by_id_query(genre_id), "Genres")
    hit = first_hit_or_404(response, "Genre not found")
    return parse_genre_detail(hit.get("_source", {}))
