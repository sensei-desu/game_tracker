
import os
import re

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# Reserved internal identifier domain; not used to send email.
LOGIN_DOMAIN = "users.nexus.invalid"


class AuthRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8, max_length=128)


def clean_username(value: str) -> str:
    username = value.strip().lower()

    if not re.fullmatch(r"[a-z0-9_]{3,20}", username):
        raise HTTPException(
            status_code=400,
            detail="Username must contain 3–20 letters, numbers, or underscores.",
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
        # Register the account with Supabase Auth.
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
            if response.status_code == 429:
                raise HTTPException(429, "Too many attempts. Try again later.")

            raise HTTPException(
                status_code=400,
                detail="Account creation failed. The username may already be taken.",
            )

        data = response.json()
        user = data.get("user") or {}
        session = data.get("access_token")

        if not user.get("id") or not session:
            raise HTTPException(
                status_code=503,
                detail="No login session was returned. Check Supabase Auth settings.",
            )

        # Create the public username profile using the user's own token.
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
            # Do not return tokens if profile setup failed.
            raise HTTPException(
                status_code=500,
                detail="Account was created, but profile setup failed. Contact support.",
            )

    return {
        "access_token": session,
        "refresh_token": data.get("refresh_token"),
        "user": {"id": user["id"], "username": username},
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
            raise HTTPException(401, "Incorrect username or password.")

        data = response.json()
        user = data.get("user") or {}
        token = data.get("access_token")

        if not user.get("id") or not token:
            raise HTTPException(401, "Login failed.")

        return {
            "access_token": token,
            "refresh_token": data.get("refresh_token"),
            "user": {
                "id": user["id"],
                "username": username,
            },
        }
