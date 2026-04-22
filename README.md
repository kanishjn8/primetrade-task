# TaskManager API

A scalable REST API with JWT authentication and role-based access control (RBAC), built with FastAPI, PostgreSQL, and Next.js. Deployed via Docker Compose.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [With Docker (recommended)](#with-docker-recommended)
  - [Local Development (without Docker)](#local-development-without-docker)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Default Users](#default-users)
- [Database Schema](#database-schema)
- [Scalability Notes](#scalability-notes)
- [Development Notes](#development-notes)

---

## Features

- User registration and login with bcrypt password hashing
- JWT access tokens (15 to 30 min configurable) and refresh tokens (7 days by default)
- Role-based access control: `user` and `admin` roles
- Full CRUD API for Tasks with ownership enforcement
- Admin users can view and manage all users and tasks
- Auto-generated Swagger UI and ReDoc documentation
- Input validation and sanitization via Pydantic v2
- Async database access via SQLAlchemy 2 + asyncpg
- Dockerized with PostgreSQL, backend, and frontend services

---

## Tech Stack

| Layer       | Technology                           |
|-------------|--------------------------------------|
| Backend     | Python 3.12, FastAPI, SQLAlchemy 2   |
| Auth        | python-jose (JWT), passlib (bcrypt)  |
| Database    | PostgreSQL 16                        |
| Migrations  | Alembic                              |
| Validation  | Pydantic v2                          |
| API Docs    | Swagger UI / ReDoc (FastAPI built-in)|
| Frontend    | Next.js 14 (App Router), TypeScript  |
| Styling     | Tailwind CSS                         |
| HTTP Client | Axios                                |
| Package Mgr | `uv` (backend), `npm` (frontend)     |
| Containers  | Docker, Docker Compose               |

---

## Project Structure

```text
project-root/
- docker-compose.yml
- .env.example
- README.md
- backend/
  - Dockerfile
  - pyproject.toml
  - schema.sql
  - alembic/
  - app/
    - main.py
    - config.py
    - database.py
    - dependencies.py
    - models/         # SQLAlchemy ORM models
    - schemas/        # Pydantic request/response schemas
    - routers/        # FastAPI route handlers
    - services/       # Business logic layer
- frontend/
  - Dockerfile
  - package.json
  - src/
    - app/            # Next.js App Router pages
    - components/     # Reusable UI components
    - lib/            # Axios instance and shared types
    - context/        # AuthContext (JWT state)
```

---

## Prerequisites

For Docker setup:
- [Docker](https://docs.docker.com/get-docker/) >= 24.x
- [Docker Compose](https://docs.docker.com/compose/) >= 2.x

For local development:
- [uv](https://docs.astral.sh/uv/getting-started/installation/) >= 0.4.x
- Python >= 3.12
- Node.js >= 20.x
- PostgreSQL >= 16

---

## Getting Started

### With Docker (recommended)

**1. Clone the repository**
```bash
git clone <repo-url>
cd project-root
```

**2. Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your local secrets and database settings.

**3. Start all services**
```bash
docker compose up --build
```

This will:
- Start PostgreSQL 16 and apply `backend/schema.sql` on first boot
- Build and start the FastAPI backend
- Build and start the Next.js frontend

**4. Access the services**

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:3000      |
| API      | http://localhost:8000      |
| Swagger  | http://localhost:8000/docs |
| ReDoc    | http://localhost:8000/redoc|

**5. Stop services**
```bash
docker compose down
docker compose down -v
```

### Local Development (without Docker)

#### Backend

**1. Install dependencies**
```bash
cd backend
uv sync
```

**2. Set up the database**
```bash
psql -U postgres -c "CREATE DATABASE appdb;"
psql -U postgres -d appdb -f schema.sql
```

**3. Configure environment**
```bash
cd ..
cp .env.example .env
```

**4. Run the backend**
```bash
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

#### Frontend

**1. Install dependencies**
```bash
cd frontend
npm install
```

**2. Configure environment**
```bash
cp .env.local.example .env.local
```

**3. Run the dev server**
```bash
npm run dev
```

Frontend will be available at http://localhost:3000.

---

## Environment Variables

Copy `.env.example` to `.env` at the project root and fill in the values.

| Variable                      | Description                                   | Example                     |
|-------------------------------|-----------------------------------------------|-----------------------------|
| `POSTGRES_USER`               | PostgreSQL username                           | `appuser`                   |
| `POSTGRES_PASSWORD`           | PostgreSQL password                           | `strongpassword`            |
| `POSTGRES_DB`                 | PostgreSQL database name                      | `appdb`                     |
| `SECRET_KEY`                  | Secret key for signing JWTs                   | `your-secret-key-here`      |
| `ALGORITHM`                   | JWT signing algorithm                         | `HS256`                     |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes              | `30`                        |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Refresh token lifetime in days                | `7`                         |
| `ALLOWED_ORIGINS`             | Comma-separated allowed frontend origins      | `http://localhost:3000`     |

> Never commit `.env` to version control.

Frontend local development uses `frontend/.env.local`:

| Variable                   | Description                          | Example                 |
|----------------------------|--------------------------------------|-------------------------|
| `NEXT_PUBLIC_API_BASE_URL` | Base URL used by the browser client  | `http://localhost:8000` |

---

## API Reference

All endpoints are prefixed with `/api/v1`. Full interactive documentation is available at `/docs`.

### Authentication - `/api/v1/auth`

| Method | Endpoint    | Auth | Description                                    |
|--------|-------------|------|------------------------------------------------|
| POST   | `/register` | -    | Register a new user and return that user.      |
| POST   | `/login`    | -    | Login and return access and refresh JWTs.      |
| POST   | `/refresh`  | -    | Refresh access and refresh JWTs from cookie.   |

**Register request body**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "StrongPass123!"
}
```

Password rules: minimum 8 characters, at least one uppercase letter, one number.

**Login response**
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

Use the access token in protected requests:

```text
Authorization: Bearer <access_token>
```

### Users - `/api/v1/users` *(admin only)*

| Method | Endpoint   | Description                    |
|--------|------------|--------------------------------|
| GET    | `/`        | List all registered users      |
| GET    | `/{id}`    | Get a specific user by ID      |
| PATCH  | `/{id}`    | Update a user's role/status    |
| DELETE | `/{id}`    | Delete a user and their tasks  |

### Tasks - `/api/v1/tasks`

| Method | Endpoint   | Description                                           |
|--------|------------|-------------------------------------------------------|
| GET    | `/`        | List tasks. Users see own tasks; admins see all.      |
| POST   | `/`        | Create a new task for the authenticated user.         |
| GET    | `/{id}`    | Get one task by ID.                                   |
| PATCH  | `/{id}`    | Update a task.                                        |
| DELETE | `/{id}`    | Delete a task.                                        |

**Create task request body**
```json
{
  "title": "Write unit tests",
  "description": "Cover auth and task service",
  "priority": "high"
}
```

**Task fields**
- `status`: `pending` | `in_progress` | `completed`
- `priority`: `low` | `medium` | `high`

### Error Responses

All errors return JSON with at least:

```json
{ "detail": "Human-readable error message" }
```

Validation errors also include a flattened `errors` object for field-level UI feedback.

| Status | Meaning                                    |
|--------|--------------------------------------------|
| 400    | Bad request                                |
| 401    | Missing or invalid JWT                     |
| 403    | Authenticated but insufficient permissions |
| 404    | Resource not found                         |
| 422    | Validation error                           |
| 500    | Internal server error                      |

---

## Default Users

There are no seeded users. Register through `POST /api/v1/auth/register`.

To promote a user to admin directly in PostgreSQL:

```sql
UPDATE users SET role = 'admin' WHERE email = 'your@email.com';
```

---

## Database Schema

The initial schema lives in `backend/schema.sql` and is also represented as an Alembic baseline migration.

Key design decisions:
- UUID primary keys for users and tasks
- PostgreSQL ENUMs for `role`, `status`, and `priority`
- `ON DELETE CASCADE` on `tasks.owner_id`
- `updated_at` maintained through PostgreSQL triggers
- Indexes on `tasks.owner_id`, `tasks.status`, and `users.email`

---

## Scalability Notes

**Horizontal scaling**: The backend is stateless. JWT access tokens are self-contained, so multiple API instances can sit behind a load balancer without shared session storage.

**Database pooling**: SQLAlchemy uses an async engine with pooling and `pool_pre_ping`. PgBouncer can be introduced later without changing route or service code.

**Extensibility**: The backend is split by models, schemas, routers, and services. Adding a new entity follows the same pattern without modifying the existing task flow.

**Migrations**: Alembic is configured for future schema changes, while `schema.sql` remains the bootstrap path for a fresh PostgreSQL instance.

---

## Development Notes

- Swagger UI is available at `/docs` and ReDoc at `/redoc`.
- The frontend stores the access token and the last-used email in `localStorage`.
- The refresh token is also set as an HTTP-only cookie by the backend.
- `uv` is the backend package manager. Use `uv sync` and `uv add`, not `pip`.
- In Docker, the frontend uses `http://localhost:8000` as its public API base URL because requests originate in the browser, not from inside the Docker network.
