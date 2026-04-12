from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    detail: str | dict[str, object]


class PageParams(BaseModel):
    page_number: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)
