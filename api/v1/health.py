from fastapi import APIRouter, HTTPException, status

from db.elasticsearch import es_manager
from db.redis import redis_manager
from utils.health import build_readiness_response

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness() -> dict[str, object]:
    es_ok = await es_manager.ping()
    redis_ok = await redis_manager.ping()
    payload = build_readiness_response(es_ok=es_ok, redis_ok=redis_ok)

    if payload["status"] != "ok":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=payload,
        )

    return payload
