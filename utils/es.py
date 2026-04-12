from elasticsearch.exceptions import TransportError
from fastapi import HTTPException, status

from db.elasticsearch import es_manager


async def search_or_503(index: str, body: dict, service_name: str) -> dict:
    try:
        return await es_manager.client.search(index=index, body=body)
    except TransportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name} storage is unavailable",
        ) from exc


def first_hit_or_404(response: dict, not_found_detail: str) -> dict:
    hits = response.get("hits", {}).get("hits", [])
    if not hits:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail)
    return hits[0]
