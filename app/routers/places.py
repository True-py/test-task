from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.art_api import fetch_artwork_by_id
from app.auth import verify_basic_auth
from app.database import get_db
from app.models import ProjectPlace
from app.schemas import PlaceCreate, PlaceRead, PlaceUpdate
from app.services import (
    get_place_or_404,
    get_project_or_404,
    update_project_completion,
    validate_no_duplicate_place,
    validate_project_places_limit,
)


router = APIRouter(
    prefix="/projects/{project_id}/places",
    tags=["project places"],
    dependencies=[Depends(verify_basic_auth)],
)


@router.post("/", response_model=PlaceRead, status_code=status.HTTP_201_CREATED)
async def add_place(
    project_id: int,
    payload: PlaceCreate,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(db, project_id)

    validate_project_places_limit(project)
    validate_no_duplicate_place(project, payload.external_id)

    artwork = await fetch_artwork_by_id(payload.external_id)

    place = ProjectPlace(
        project_id=project.id,
        external_id=artwork["external_id"],
        title=artwork["title"],
        artist_display=artwork["artist_display"],
        image_id=artwork["image_id"],
        notes=payload.notes,
    )

    db.add(place)
    db.commit()
    db.refresh(place)

    update_project_completion(db, project)

    return place


@router.get("/", response_model=list[PlaceRead])
def list_places(
    project_id: int,
    visited: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    get_project_or_404(db, project_id)

    query = select(ProjectPlace).where(
        ProjectPlace.project_id == project_id
    )

    if visited is not None:
        query = query.where(ProjectPlace.visited == visited)

    query = query.order_by(ProjectPlace.id.desc())
    query = query.offset(skip).limit(limit)

    places = db.scalars(query).all()

    return places


@router.get("/{place_id}", response_model=PlaceRead)
def get_place(
    project_id: int,
    place_id: int,
    db: Session = Depends(get_db),
):
    place = get_place_or_404(db, project_id, place_id)

    return place


@router.patch("/{place_id}", response_model=PlaceRead)
def update_place(
    project_id: int,
    place_id: int,
    payload: PlaceUpdate,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(db, project_id)
    place = get_place_or_404(db, project_id, place_id)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(place, field, value)

    db.add(place)
    db.commit()
    db.refresh(place)

    update_project_completion(db, project)
    db.refresh(place)

    return place


@router.patch("/{place_id}/visited", response_model=PlaceRead)
def mark_place_as_visited(
    project_id: int,
    place_id: int,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(db, project_id)
    place = get_place_or_404(db, project_id, place_id)

    place.visited = True

    db.add(place)
    db.commit()
    db.refresh(place)

    update_project_completion(db, project)
    db.refresh(place)

    return place