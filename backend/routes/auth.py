
import os
import re

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


class AuthRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8, max_length=128)


def validate_username(username: str) -> str:
    username = username.strip()

    if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
        raise HTTPException(
            status_code=400,
            detail="Username must be 3–20 characters using letters, numbers, or underscores.",
        )

    return username


@router.post("/signup")
async def signup(payload: AuthRequest):
    raise HTTPException(
        status_code=501,
        detail="Signup will be enabled after the secure username authentication mapping is configured.",
    )


@router.post("/login")
async def login(payload: AuthRequest):
    raise HTTPException(
        status_code=501,
        detail="Login will be enabled after the secure username authentication mapping is configured.",
    )

