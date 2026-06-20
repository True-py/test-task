from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import places, projects


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.app_name,
    description=(
        "CRUD API for managing travel projects and places "
        "from the Art Institute of Chicago API."
    ),
    version=settings.app_version,
    debug=settings.debug,
)


app.include_router(projects.router, prefix="/api/v1")
app.include_router(places.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
    }