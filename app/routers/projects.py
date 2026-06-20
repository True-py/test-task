from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.art_api import fetch_artwork_by_id
from app.auth import verify_basic_auth
from app.database import get_db
from app.models import ProjectPlace, TravelProject
from app.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.services import (
    get_project_or_404,
    update_project_completion,
)


router = APIRouter(
    prefix="/projects",
    tags=["travel projects"],
    dependencies=[Depends(verify_basic_auth)],
)


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
):
    project = TravelProject(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    if payload.places:
        seen_external_ids = set()

        for place_payload in payload.places:
            if place_payload.external_id in seen_external_ids:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Duplicate places are not allowed",
                )

            seen_external_ids.add(place_payload.external_id)

            artwork = await fetch_artwork_by_id(place_payload.external_id)

            place = ProjectPlace(
                project_id=project.id,
                external_id=artwork["external_id"],
                title=artwork["title"],
                artist_display=artwork["artist_display"],
                image_id=artwork["image_id"],
                notes=place_payload.notes,
            )

            db.add(place)

        db.commit()
        db.refresh(project)

    update_project_completion(db, project)

    return project


@router.get("/", response_model=list[ProjectRead])
def list_projects(
    completed: bool | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(TravelProject).options(
        selectinload(TravelProject.places)
    )

    if completed is not None:
        query = query.where(TravelProject.completed == completed)

    if search:
        query = query.where(
            TravelProject.name.ilike(f"%{search}%")
        )

    query = query.order_by(TravelProject.id.desc())
    query = query.offset(skip).limit(limit)

    projects = db.scalars(query).all()

    return projects


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.scalar(
        select(TravelProject)
        .options(selectinload(TravelProject.places))
        .where(TravelProject.id == project_id)
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(db, project_id)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(project, field, value)

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(db, project_id)

    if any(place.visited for place in project.places):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Project cannot be deleted because "
                "at least one place is already marked as visited"
            ),
        )

    db.delete(project)
    db.commit()

    return None