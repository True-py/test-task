# Travel Planner API

A FastAPI backend application for managing travel projects and places from the Art Institute of Chicago API.

The project supports CRUD operations for travel projects, adding external places, updating notes, marking places as visited, and automatically completing a project when all places are visited.

---

## Tech Stack

* Python 3.12
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* httpx
* Docker
* Docker Compose

---

## Features

* CRUD for travel projects
* Add places from the Art Institute of Chicago API
* Create a project with places in one request
* Update notes for places
* Mark places as visited
* Automatically mark project as completed when all places are visited
* Prevent deleting a project if any place is already visited
* Prevent duplicate places in one project
* Limit each project to a maximum of 10 places
* Pagination and filtering
* External API response caching
* Optional Basic Authentication

---

## Environment Variables

Create a `.env` file from `.env.example`.

```env
APP_NAME=Travel Planner API
APP_VERSION=1.0.0
ENVIRONMENT=local
DEBUG=true

DATABASE_URL=sqlite:///./travel_planner.db

ART_API_BASE_URL=https://api.example.com/api/...
ART_API_TIMEOUT_SECONDS=10
CACHE_TTL_SECONDS=600

REQUIRE_AUTH=false
API_USERNAME=admin
API_PASSWORD=admin123
```

`.env` should not be committed to GitHub.

---

## Local Setup

```bash
python -m venv .venv
```

Activate virtual environment:

```bash
source .venv/bin/activate
```

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`:

```bash
cp .env.example .env
```

For Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Run application:

```bash
uvicorn app.main:app --reload
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## Docker Setup

Build and run:

```bash
docker compose up --build
```

Stop containers:

```bash
docker compose down
```

---

## API Endpoints

Base API URL:

```text
/api/v1
```

### Projects

```http
POST   /api/v1/projects/
GET    /api/v1/projects/
GET    /api/v1/projects/{project_id}
PATCH  /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
```

### Places

```http
POST   /api/v1/projects/{project_id}/places/
GET    /api/v1/projects/{project_id}/places/
GET    /api/v1/projects/{project_id}/places/{place_id}
PATCH  /api/v1/projects/{project_id}/places/{place_id}
PATCH  /api/v1/projects/{project_id}/places/{place_id}/visited
```

---

## Example Requests

Create project:

```json
{
  "name": "Chicago Art Trip",
  "description": "Places to visit in Chicago",
  "start_date": "2026-07-01"
}
```

Add place:

```json
{
  "external_id": 129884,
  "notes": "Must see artwork"
}
```

Update place notes:

```json
{
  "notes": "Updated note"
}
```

---

## Business Rules

* A project can contain maximum 10 places.
* The same place cannot be added twice to one project.
* A place is validated through the Art Institute of Chicago API before saving.
* A project becomes completed when all its places are marked as visited.
* A project cannot be deleted if at least one place is already visited.

External API endpoint:

```text
https://api.example.com/api/v1/artworks/{id}
```

---

## Optional Basic Authentication

Basic Authentication is disabled by default.

To enable it:

```env
REQUIRE_AUTH=true
```

Default credentials:

```env
API_USERNAME=admin
API_PASSWORD=admin123
```

---

## Notes

SQLite is used for simplicity because this is a test task.

For production, PostgreSQL and database migrations with Alembic would be a better choice.
