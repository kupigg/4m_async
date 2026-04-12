from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Genre(BaseModel):
    id: UUID
    description: str
    created_at: datetime | None = None


class GenreListItem(BaseModel):
    uuid: UUID
    name: str
    description: str | None = None


class GenreDetailItem(BaseModel):
    uuid: UUID
    name: str
    description: str | None = None
