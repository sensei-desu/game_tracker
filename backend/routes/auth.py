
import os
import re

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# Internal identifier used for Supabase Auth.
LOGIN_DOMAIN = "users.nexus.invalid"


class AuthRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=3, max_length=128)


def clean_username(value: str) -> str:
    username = value.strip().lower()

    if not re.fullmatch(r"[a-z0-9_]{3,20}", username):
        raise HTTPException(
            status_code=400,
            detail=(
                "Username must contain 3–20 characters: "
                "letters, numbers, or underscores."
            ),
        )

    return username


def internal_login(username: str) -> str:
    return f"{username}@{LOGIN_DOMAIN}"


def config():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured.",
        )

    return {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
    }


@router.post("/signup")
async def signup(payload: AuthRequest):
    username = clean_username(payload.username)
    headers = config()

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers=headers,
            json={
                "email": internal_login(username),
                "password": payload.password,
                "data": {"username": username},
            },
        )

        if response.status_code >= 400:
            # Keep the provider's diagnostic in Render logs.
            print(
                "Supabase signup error:",
                response.status_code,
                response.text,
            )
            raise HTTPException(
                status_code=400,
                detail=(
                    "Signup failed. The username may already exist, "
                    "or Supabase rejected the internal login identifier. "
                    "Check the backend logs."
                ),
            )

        data = response.json()
        user = data.get("user") or {}
        session = data.get("access_token")

        if not user.get("id"):
            raise HTTPException(
                status_code=502,
                detail="Supabase did not return a user.",
            )

        if not session:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Supabase created or recognized the account but did not "
                    "return a session. Check your Supabase Auth settings."
                ),
            )

        profile_response = await client.post(
            f"{SUPABASE_URL}/rest/v1/profiles",
            headers={
                **headers,
                "Authorization": f"Bearer {session}",
                "Prefer": "return=minimal",
            },
            json={
                "id": user["id"],
                "username": username,
            },
        )

        if profile_response.status_code >= 400:
            print(
                "Supabase profile error:",
                profile_response.status_code,
                profile_response.text,
            )
            raise HTTPException(
                status_code=500,
                detail=(
                    "Account authentication succeeded, but profile creation "
                    "failed. Check the backend logs."
                ),
            )

    return {
        "access_token": session,
        "refresh_token": data.get("refresh_token"),
        "user": {
            "id": user["id"],
            "username": username,
        },
    }


@router.post("/login")
async def login(payload: AuthRequest):
    username = clean_username(payload.username)
    headers = config()

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers=headers,
            json={
                "email": internal_login(username),
                "password": payload.password,
            },
        )

        if response.status_code >= 400:
            print(
                "Supabase login error:",
                response.status_code,
                response.text,
            )
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password.",
            )

        data = response.json()
        user = data.get("user") or {}
        token = data.get("access_token")

        if not user.get("id") or not token:
            raise HTTPException(
                status_code=401,
                detail="Login failed. No valid session was returned.",
            )

        # Read the saved username from the user's profile.
        profile_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/profiles",
            headers={
                **headers,
                "Authorization": f"Bearer {token}",
            },
            params={
                "select": "username",
                "id": f"eq.{user['id']}",
                "limit": "1",
            },
        )

        if profile_response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail="Could not retrieve your username profile.",
            )

        profiles = profile_response.json()

        if not profiles:
            raise HTTPException(
                status_code=403,
                detail="Your account profile is missing. Contact support.",
            )

        return {
            "access_token": token,
            "refresh_token": data.get("refresh_token"),
            "user": {
                "id": user["id"],
                "username": profiles[0]["username"],
            },
        }
