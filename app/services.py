from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ProjectPlace, TravelProject


MAX_PLACES_PER_PROJECT = 10


def get_project_or_404(db: Session, project_id: int) -> TravelProject:
    project = db.get(TravelProject, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


def get_place_or_404(
    db: Session,
    project_id: int,
    place_id: int,
) -> ProjectPlace:
    place = db.scalar(
        select(ProjectPlace).where(
            ProjectPlace.id == place_id,
            ProjectPlace.project_id == project_id,
        )
    )

    if not place:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place not found",
        )

    return place


def validate_project_places_limit(
    project: TravelProject,
    additional_count: int = 1,
) -> None:
    current_count = len(project.places)

    if current_count + additional_count > MAX_PLACES_PER_PROJECT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A project can contain maximum {MAX_PLACES_PER_PROJECT} places",
        )


def validate_no_duplicate_place(
    project: TravelProject,
    external_id: int,
) -> None:
    if any(place.external_id == external_id for place in project.places):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This place already exists in the project",
        )


def update_project_completion(
    db: Session,
    project: TravelProject,
) -> None:
    places = project.places

    project.completed = bool(places) and all(
        place.visited for place in places
    )

    db.add(project)
    db.commit()
    db.refresh(project)