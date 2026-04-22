"""Authentication routes for user registration and login workflows."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import User, UserRole
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserRead
from app.services import (
    REFRESH_COOKIE_NAME,
    REFRESH_TOKEN_TYPE,
    authenticate_user,
    build_token_subject,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Attach the refresh token as an HTTP-only cookie for browser clients."""

    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with the default `user` role.",
    responses={
        400: {"description": "The email or username is already registered."},
        422: {"description": "The request body failed validation."},
    },
)
async def register(
    payload: Annotated[UserCreate, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRead:
    """Register a new user after enforcing unique email and username constraints."""

    result = await db.execute(
        select(User).where(or_(User.email == payload.email, User.username == payload.username))
    )
    existing_user = result.scalar_one_or_none()
    if existing_user is not None:
        if existing_user.email == payload.email:
            detail = "Email is already registered."
        else:
            detail = "Username is already taken."
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    user = User(
        email=str(payload.email),
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=UserRole.USER,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate a user",
    description="Validate credentials and return access and refresh JWT tokens.",
    responses={
        401: {"description": "The provided credentials are invalid."},
        422: {"description": "The request body failed validation."},
    },
)
async def login(
    response: Response,
    payload: Annotated[LoginRequest, Body(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Authenticate the user and issue a fresh token pair."""

    user = await authenticate_user(db, str(payload.email), payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token_subject = build_token_subject(user)
    access_token = create_access_token(token_subject)
    refresh_token = create_refresh_token(token_subject)
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh JWT tokens",
    description="Issue a new access token and refresh token using the refresh token cookie.",
    responses={401: {"description": "The refresh token is missing or invalid."}},
)
async def refresh_tokens(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Refresh a user session from the HTTP-only refresh token cookie."""

    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if raw_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token cookie is missing.")

    try:
        token_payload = decode_token(raw_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    if token_payload.type != REFRESH_TOKEN_TYPE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")

    try:
        user_id = UUID(token_payload.sub)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token subject.") from exc

    user = await db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive or not found.")

    token_subject = build_token_subject(user)
    access_token = create_access_token(token_subject)
    refresh_token = create_refresh_token(token_subject)
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
