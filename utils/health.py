def build_readiness_response(es_ok: bool, redis_ok: bool) -> dict[str, object]:
    return {
        "status": "ok" if es_ok and redis_ok else "degraded",
        "services": {
            "elasticsearch": "ok" if es_ok else "unavailable",
            "redis": "ok" if redis_ok else "unavailable",
        },
    }
