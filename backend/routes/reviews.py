
import os
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/reviews", tags=["Reviews"])

bearer_scheme = HTTPBearer(auto_error=False)

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")


class ReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text: str = Field(min_length=10, max_length=1000)


def config():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=503,
            detail="Review service is not configured.",
        )

    return {"apikey": SUPABASE_KEY}


async def authenticated_user(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Please log in to submit a review.",
        )

    token = authorization.removeprefix("Bearer ").strip()

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                **config(),
                "Authorization": f"Bearer {token}",
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Your session is invalid or expired. Please log in again.",
        )

    user = response.json()

    if not user.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Could not verify your account.",
        )

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
                "select": (
    "id,user_id,username,rating,review_text,"
    "created_at,updated_at"
),
                "order": "created_at.desc",
            },
        )

    if response.status_code >= 400:
        print("Supabase list reviews error:", response.status_code, response.text)
        raise HTTPException(
            status_code=502,
            detail="Could not load reviews.",
        )

    return response.json()


@router.post("")
async def submit_review(
    payload: ReviewRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    authorization: str | None = Header(default=None),
):
    # Prefer Swagger's Bearer authentication credentials when provided.
    if credentials:
        authorization = (
            f"{credentials.scheme} {credentials.credentials}"
        )

    user = await authenticated_user(authorization)
    user_id = str(UUID(user["id"]))

    async with httpx.AsyncClient(timeout=15) as client:
        # Retrieve the username associated with the authenticated user.
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
            print(
                "Supabase profile lookup error:",
                profile_response.status_code,
                profile_response.text,
            )
            raise HTTPException(
                status_code=502,
                detail="Could not load your profile.",
            )

        profiles = profile_response.json()

        if not profiles:
            raise HTTPException(
                status_code=400,
                detail="Your account profile is missing.",
            )

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
            status_code=409,
            detail=(
                "You already submitted a review. "
                "Editing will be available on the Reviews page."
            ),
        )

    if response.status_code >= 400:
        print(
            "Supabase submit review error:",
            response.status_code,
            response.text,
        )
        raise HTTPException(
            status_code=502,
            detail="Could not submit your review.",
        )

    saved_reviews = response.json()

    if not saved_reviews:
        raise HTTPException(
            status_code=502,
            detail="The review was not returned after submission.",
        )

    return {"review": saved_reviews[0]}
    
@router.delete("/{review_id}")
async def delete_review(
    review_id: UUID,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    authorization: str | None = Header(default=None),
):
    # Get the logged-in user's access token.
    if credentials:
        authorization = (
            f"{credentials.scheme} {credentials.credentials}"
        )

    # Verify the user's Supabase session.
    user = await authenticated_user(authorization)
    user_id = str(UUID(user["id"]))

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.delete(
            f"{SUPABASE_URL}/rest/v1/reviews",
            headers={
                **config(),
                "Authorization": authorization,
                "Prefer": "return=representation",
            },
            params={
                "id": f"eq.{str(review_id)}",
                "user_id": f"eq.{user_id}",
                "select": "id",
            },
        )

    if response.status_code >= 400:
        print(
            "Supabase delete review error:",
            response.status_code,
            response.text,
        )
        raise HTTPException(
            status_code=502,
            detail="Could not delete your review.",
        )

    deleted_reviews = response.json()

    if not deleted_reviews:
        raise HTTPException(
            status_code=404,
            detail="Review not found, or you cannot delete it.",
        )

    return {
        "message": "Review deleted successfully.",
        "deleted_id": str(review_id),
    }

