
import os
from uuid import UUID

import httpx
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")


class ReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text: str = Field(min_length=0, max_length=1000)


def config():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(503, "Review service is not configured.")

    return {"apikey": SUPABASE_KEY}


async def authenticated_user(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Please log in to submit a review.")

    token = authorization.removeprefix("Bearer ").strip()

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={**config(), "Authorization": f"Bearer {token}"},
        )

    if response.status_code != 200:
        raise HTTPException(401, "Your session is invalid or expired.")

    user = response.json()
    if not user.get("id"):
        raise HTTPException(401, "Could not verify your account.")

    return user


@router.get("")
async def list_reviews():
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/reviews",
            headers={
                **config(),
                "Accept": "application/json",
            },
            params={
                "select": "id,username,rating,review_text,created_at,updated_at",
                "order": "created_at.desc",
            },
        )

    if response.status_code >= 400:
        raise HTTPException(502, "Could not load reviews.")

    return response.json()


@router.post("")
async def submit_review(
    payload: ReviewRequest,
    authorization: str | None = Header(default=None),
):
    user = await authenticated_user(authorization)
    user_id = str(UUID(user["id"]))

    async with httpx.AsyncClient(timeout=15) as client:
        # Get the username from the authenticated user's own profile.
        profile_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/profiles",
            headers={
                **config(),
                "Authorization": authorization,
            },
            params={
                "select": "username",
                "id": f"eq.{user_id}",
                "limit": "1",
            },
        )

        if profile_response.status_code >= 400:
            raise HTTPException(502, "Could not load your profile.")

        profiles = profile_response.json()
        if not profiles:
            raise HTTPException(400, "Your account profile is missing.")

        username = profiles[0]["username"]

        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/reviews",
            headers={
                **config(),
                "Authorization": authorization,
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            json={
                "user_id": user_id,
                "username": username,
                "rating": payload.rating,
                "review_text": payload.review_text.strip(),
            },
        )

    if response.status_code == 409:
        raise HTTPException(
            409,
            "You already submitted a review. Editing will be available on the Reviews page.",
        )

    if response.status_code >= 400:
        raise HTTPException(502, "Could not submit your review.")

    return {"review": response.json()[0]}

