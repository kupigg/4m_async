import hashlib
import json

from elasticsearch.exceptions import TransportError
from fastapi import HTTPException, status

from core.settings import get_settings
from db.elasticsearch import es_manager
from db.redis import redis_manager


def _cache_key(index: str, body: dict) -> str:
    payload = json.dumps({"index": index, "body": body}, sort_keys=True, default=str)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"es-search:{digest}"


async def search_or_503(index: str, body: dict, service_name: str) -> dict:
    settings = get_settings()
    key = _cache_key(index, body)

    try:
        cached = await redis_manager.client.get(key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass

    try:
        response = dict(await es_manager.client.search(index=index, body=body))
    except TransportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service_name} storage is unavailable",
        ) from exc

    try:
        await redis_manager.client.setex(key, settings.redis.cache_ttl, json.dumps(response, default=str))
    except Exception:
        pass

    return response


def first_hit_or_404(response: dict, not_found_detail: str) -> dict:
    hits = response.get("hits", {}).get("hits", [])
    if not hits:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=not_found_detail)
    return hits[0]
