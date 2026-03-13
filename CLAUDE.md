# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
MigrantsBridge is an AI-driven business operations platform for an organization providing immigration services, community support, job placement, and wealth creation for migrants.

## Tech Stack
- Backend: Python 3.12+ / FastAPI / SQLAlchemy 2.0 / Alembic / Celery / Redis
- Frontend: Next.js 14 (App Router) / TypeScript / Tailwind CSS / shadcn/ui
- Database: PostgreSQL 16
- AI: Claude API (Anthropic) for workflow generation, document classification, eligibility assessment
- Infrastructure: Docker Compose for local dev

## Build & Run Commands
```bash
# Start all services
docker compose up -d

# Backend only
cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload

# Frontend only
cd frontend && npm install && npm run dev

# Run backend tests
cd backend && pytest

# Run single test
cd backend && pytest tests/test_api/test_clients.py -v

# Run frontend tests
cd frontend && npm test

# Database migrations
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "description"

# Celery worker
cd backend && celery -A app.core.celery_app worker -l info

# Celery beat (scheduler)
cd backend && celery -A app.core.celery_app beat -l info
```

## Architecture
- **Backend**: Modular service-layer architecture. API routes in `app/api/v1/`, business logic in `app/services/`, SQLAlchemy models in `app/models/`, Pydantic schemas in `app/schemas/`. Celery tasks in `app/workers/`. Claude API integration in `app/integrations/claude.py` with prompt templates in `app/prompts/`.
- **Frontend**: Next.js App Router with route groups: `(auth)` for login, `(portal)` for public intake, `(dashboard)` for authenticated app. Server state via TanStack Query, client state via Zustand. Components split into `ui/` (shadcn primitives), `shared/` (reusable), `features/` (domain-specific).
- **AI Workflow Engine**: Claude analyzes business process descriptions and auto-generates workflow definitions (trigger + steps + conditions). Workflows execute asynchronously via Celery. Models: `workflows`, `workflow_steps`, `workflow_executions`, `workflow_step_logs`.
- **RBAC**: Role-based access control. Backend enforces via FastAPI dependencies. Frontend uses `<Can>` component and `usePermission` hook.
- **All models use UUID PKs, soft deletes, and timestamp mixins.**

## Key Conventions
- Backend API versioned at `/api/v1/`
- Pydantic schemas suffixed: `Create`, `Read`, `Update` (e.g., `ClientCreate`, `ClientRead`)
- Services receive `AsyncSession` and encapsulate all DB logic
- Celery tasks are in `app/workers/` and auto-discovered
- Frontend query hooks in `src/hooks/queries/`, services in `src/services/`
- Zod validation schemas in `src/lib/validations/`
