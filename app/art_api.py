import time
from dataclasses import dataclass

import httpx
from fastapi import HTTPException, status

from app.config import settings


@dataclass
class CachedItem:
    expires_at: float
    value: dict


_cache: dict[int, CachedItem] = {}


async def fetch_artwork_by_id(external_id: int) -> dict:
    cached = _cache.get(external_id)

    if cached and cached.expires_at > time.time():
        return cached.value

    url = f"{settings.art_api_base_url}/{external_id}"

    try:
        async with httpx.AsyncClient(
            timeout=settings.art_api_timeout_seconds
        ) as client:
            response = await client.get(url)

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Art Institute API is unavailable: {exc}",
        ) from exc

    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place was not found in the Art Institute API",
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Art Institute API returned an error",
        )

    payload = response.json()
    artwork = payload.get("data")

    if not artwork:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Place was not found in the Art Institute API",
        )

    result = {
        "external_id": artwork.get("id"),
        "title": artwork.get("title") or "Untitled",
        "artist_display": artwork.get("artist_display"),
        "image_id": artwork.get("image_id"),
    }

    _cache[external_id] = CachedItem(
        expires_at=time.time() + settings.cache_ttl_seconds,
        value=result,
    )

    return result
