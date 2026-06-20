from datetime import date, datetime

from pydantic import BaseModel, Field


class PlaceCreate(BaseModel):
    external_id: int = Field(
        ...,
        gt=0,
        description="Artwork ID from the Art Institute of Chicago",
    )
    notes: str | None = None


class PlaceUpdate(BaseModel):
    notes: str | None = None
    visited: bool | None = None


class PlaceRead(BaseModel):
    id: int
    project_id: int
    external_id: int
    title: str
    artist_display: str | None
    image_id: str | None
    notes: str | None
    visited: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    start_date: date | None = None

    places: list[PlaceCreate] | None = Field(
        default=None,
        max_length=10,
    )


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_date: date | None = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str | None
    start_date: date | None
    completed: bool
    created_at: datetime
    updated_at: datetime | None = None
    places: list[PlaceRead] = []

    model_config = {
        "from_attributes": True
    }