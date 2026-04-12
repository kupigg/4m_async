from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.v1 import router as v1_router
from core.settings import get_settings
from db.elasticsearch import es_manager
from db.redis import redis_manager
from utils.logger import setup_logging

settings = get_settings()
setup_logging()

openapi_tags = [
    {"name": "health", "description": "Service liveness/readiness checks."},
    {"name": "films", "description": "Popular films, film search and film details."},
    {"name": "persons", "description": "Person search, person details and person films."},
    {"name": "genres", "description": "Genres list and genre details."},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await es_manager.init()
    await redis_manager.init()
    try:
        yield
    finally:
        await redis_manager.close()
        await es_manager.close()


app = FastAPI(
    title=settings.app.project_name,
    description="Async cinema API for anonymous clients (v1).",
    version="1.0.0",
    debug=settings.app.debug,
    lifespan=lifespan,
    openapi_tags=openapi_tags,
)
app.include_router(v1_router, prefix=settings.app.api_v1_prefix)
