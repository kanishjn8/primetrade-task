"""FastAPI application entrypoint for TaskManager."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings
from app.database import engine
from app.routers import auth, tasks, users


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Verify database connectivity before serving requests."""

    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))
    yield


def _format_validation_errors(exc: RequestValidationError) -> dict[str, str]:
    """Convert FastAPI validation details into a flat field-error mapping."""

    errors: dict[str, str] = {}
    for error in exc.errors():
        location = [str(part) for part in error.get("loc", []) if part != "body"]
        field_name = ".".join(location) or "non_field_error"
        errors[field_name] = error.get("msg", "Invalid value.")
    return errors


app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    description=(
        "Scalable REST API for task management with JWT authentication and role-based access control. "
        "Use the `/api/v1/auth/login` endpoint to obtain a bearer token and authorize protected routes."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "auth", "description": "Authentication and token management endpoints."},
        {"name": "users", "description": "Admin-only user management endpoints."},
        {"name": "tasks", "description": "Authenticated task CRUD endpoints."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Return HTTP errors in the consistent JSON detail format."""

    detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Return validation errors with a summary detail and flattened field map."""

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error.", "errors": _format_validation_errors(exc)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Convert unhandled exceptions into a generic 500 response."""

    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error."})


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(users.router, prefix=settings.api_v1_prefix)
app.include_router(tasks.router, prefix=settings.api_v1_prefix)
