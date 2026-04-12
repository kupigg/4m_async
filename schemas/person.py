from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PersonBase(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    film_ids: list[UUID] = Field(default_factory=list)
    created_at: datetime | None = None


class Actor(PersonBase):
    pass


class Director(PersonBase):
    pass


class Writer(PersonBase):
    pass


class PersonFilmItem(BaseModel):
    uuid: UUID
    roles: list[str] = Field(default_factory=list)


class PersonSearchItem(BaseModel):
    uuid: UUID
    full_name: str
    films: list[PersonFilmItem] = Field(default_factory=list)


class PersonDetailItem(BaseModel):
    uuid: UUID
    full_name: str
    films: list[PersonFilmItem] = Field(default_factory=list)
