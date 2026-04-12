from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from schemas.genre import Genre
from schemas.person import Actor, Director, Writer


class Film(BaseModel):
    id: UUID
    title: str
    description: str
    creation_date: date
    directors: list[Director] = Field(default_factory=list)
    actors: list[Actor] = Field(default_factory=list)
    writers: list[Writer] = Field(default_factory=list)
    genres: list[Genre] = Field(default_factory=list)
    file_url: HttpUrl | None = None
    created_at: datetime | None = None


class FilmListItem(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None = None


class FilmGenreItem(BaseModel):
    uuid: UUID
    name: str


class FilmPersonItem(BaseModel):
    uuid: UUID
    full_name: str


class FilmDetailItem(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float | None = None
    description: str | None = None
    genre: list[FilmGenreItem] = Field(default_factory=list)
    actors: list[FilmPersonItem] = Field(default_factory=list)
    writers: list[FilmPersonItem] = Field(default_factory=list)
    directors: list[FilmPersonItem] = Field(default_factory=list)
