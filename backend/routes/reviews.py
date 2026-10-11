
import os
import re
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


def normalize_authorization(
    credentials: HTTPAuthorizationCredentials | None,
    authorization: str | None,
) -> str | None:
    if credentials:
        return f"{credentials.scheme} {credentials.credentials}"

    if authorization and authorization.startswith("Bearer "):
        return authorization

    return None


async def authenticated_user(authorization: str | None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Please sign in with Google to submit a review.",
        )

    token = authorization.removeprefix("Bearer ").strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing access token. Please sign in again.",
        )

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    **config(),
                    "Authorization": f"Bearer {token}",
                },
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not verify your session with Supabase.",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Your session is invalid or expired. Please sign in again.",
        )

    user = response.json()

    if not user.get("id"):
        raise HTTPException(
            status_code=401,
            detail="Could not verify your account.",
        )

    return user


async def get_or_create_profile(
    user: dict,
    authorization: str,
) -> str:
    """Return the user's profile username, creating a profile if needed."""
    try:
        user_id = str(UUID(user["id"]))
    except (KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid user account.",
        )

    headers = {
        **config(),
        "Authorization": authorization,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # First, look for an existing profile.
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/profiles",
                headers=headers,
                params={
                    "select": "username",
                    "id": f"eq.{user_id}",
                    "limit": "1",
                },
            )

            if response.status_code >= 400:
                print(
                    "Supabase profile lookup error:",
                    response.status_code,
                    response.text,
                )
                raise HTTPException(
                    status_code=502,
                    detail="Could not load your profile.",
                )

            profiles = response.json()

            if profiles and profiles[0].get("username"):
                return profiles[0]["username"]

            # Generate a username from Google metadata or the email.
            metadata = user.get("user_metadata") or {}
            email = user.get("email") or ""

            raw_name = (
                metadata.get("preferred_username")
                or metadata.get("user_name")
                or metadata.get("full_name")
                or metadata.get("name")
                or email.split("@")[0]
                or "gamer"
            )

            base = re.sub(
                r"[^a-z0-9_]",
                "",
                str(raw_name).lower(),
            )[:11] or "gamer"

            # The ID suffix reduces collisions between Google users.
            username = f"{base}_{user_id.replace('-', '')[:8]}"

            # Create the profile using the signed-in user's token.
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/profiles",
                headers={
                    **headers,
                    "Prefer": "return=representation",
                },
                json={
                    "id": user_id,
                    "username": username,
                },
            )

            if response.status_code >= 400:
                print(
                    "Supabase profile creation error:",
                    response.status_code,
                    response.text,
                )

                # A concurrent request may have created the profile.
                if response.status_code == 409:
                    retry = await client.get(
                        f"{SUPABASE_URL}/rest/v1/profiles",
                        headers=headers,
                        params={
                            "select": "username",
                            "id": f"eq.{user_id}",
                            "limit": "1",
                        },
                    )

                    if retry.status_code == 200:
                        existing = retry.json()
                        if existing and existing[0].get("username"):
                            return existing[0]["username"]

                raise HTTPException(
                    status_code=502,
                    detail=(
                        "Could not create your profile. Check the "
                        "profiles table permissions and username constraints."
                    ),
                )

            saved_profiles = response.json()

            if saved_profiles and saved_profiles[0].get("username"):
                return saved_profiles[0]["username"]

            # Some PostgREST configurations may not return the inserted row.
            retry = await client.get(
                f"{SUPABASE_URL}/rest/v1/profiles",
                headers=headers,
                params={
                    "select": "username",
                    "id": f"eq.{user_id}",
                    "limit": "1",
                },
            )

            if retry.status_code == 200:
                existing = retry.json()
                if existing and existing[0].get("username"):
                    return existing[0]["username"]

            raise HTTPException(
                status_code=502,
                detail="The profile was created but could not be retrieved.",
            )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to Supabase to load your profile.",
        )


@router.get("")
async def list_reviews():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=503,
            detail="Review service is not configured.",
        )

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/reviews",
                headers={
                    **config(),
                    "Accept": "application/json",
                },
                params={
                    "select": (
                        "id,username,rating,review_text,"
                        "created_at,updated_at"
                    ),
                    "order": "created_at.desc",
                },
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to Supabase to load reviews.",
        )

    if response.status_code >= 400:
        print(
            "Supabase list reviews error:",
            response.status_code,
            response.text,
        )
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
    authorization = normalize_authorization(
        credentials,
        authorization,
    )

    # Validate the session with Supabase Auth.
    user = await authenticated_user(authorization)

    # Create a profile automatically for first-time Google users.
    username = await get_or_create_profile(
        user,
        authorization,
    )

    user_id = str(UUID(user["id"]))

    try:
        async with httpx.AsyncClient(timeout=15) as client:
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
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to Supabase to submit your review.",
        )

    if response.status_code == 409:
        raise HTTPException(
            status_code=409,
            detail=(
                "You have already submitted a review. "
                "Editing requires a separate update endpoint."
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
