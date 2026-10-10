from pydantic import BaseModel, Field


class PageParams(BaseModel):
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0, le=10_000)


class Page[ItemT](BaseModel):
    items: list[ItemT]
    has_more: bool
