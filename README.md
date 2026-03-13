# MigrantsBridge

AI-driven business operations platform for an organization providing immigration services, community support, job placement, and wealth creation for migrants.

## Tech Stack

| Layer          | Technology                                              |
| -------------- | ------------------------------------------------------- |
| Backend        | Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic, Celery |
| Frontend       | Next.js 14 (App Router), TypeScript, Tailwind, shadcn/ui |
| Database       | PostgreSQL 16                                           |
| Cache / Broker | Redis 7                                                 |
| AI             | Claude API (Anthropic)                                  |
| Infrastructure | Docker Compose                                          |

## Quick Start

### Prerequisites

- Docker and Docker Compose v2
- (Optional) Python 3.12+, Node.js 20+ for local development without Docker

### Setup

```bash
# Clone the repository
git clone <repo-url> && cd migrantsbridge

# Copy environment file and edit values
cp .env.example .env

# Start all services
make up

# Run database migrations
make migrate
```

The application will be available at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API docs (Swagger)**: http://localhost:8000/docs

### Useful Commands

```bash
make help            # List all available make targets
make up              # Start all services
make down            # Stop all services
make logs            # Tail logs
make test            # Run all tests
make lint            # Run linters
make migrate         # Apply database migrations
make shell-backend   # Open a shell in the backend container
make shell-frontend  # Open a shell in the frontend container
```

## Architecture

```
migrantsbridge/
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── api/v1/           # Versioned API routes
│   │   ├── core/             # Config, security, celery setup
│   │   ├── integrations/     # External service clients (Claude API)
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── prompts/          # Claude prompt templates
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic layer
│   │   └── workers/          # Celery task definitions
│   ├── alembic/              # Database migrations
│   └── tests/
├── frontend/                 # Next.js application
│   └── src/
│       ├── app/              # App Router pages & layouts
│       │   ├── (auth)/       # Login / registration
│       │   ├── (portal)/     # Public intake forms
│       │   └── (dashboard)/  # Authenticated application
│       ├── components/
│       │   ├── ui/           # shadcn/ui primitives
│       │   ├── shared/       # Reusable components
│       │   └── features/     # Domain-specific components
│       ├── hooks/queries/    # TanStack Query hooks
│       ├── lib/validations/  # Zod schemas
│       └── services/         # API client functions
├── docker-compose.yml
├── Makefile
└── CLAUDE.md                 # AI coding assistant guidance
```

## Modules

| Module               | Description                                                                 |
| -------------------- | --------------------------------------------------------------------------- |
| **Client Intake**    | Multi-step intake forms, document upload, eligibility pre-screening         |
| **Case Management**  | Track immigration cases, deadlines, status updates, and document checklists |
| **Job Placement**    | Job board, employer matching, application tracking                          |
| **Community Hub**    | Events, resource directory, peer networking                                 |
| **Wealth Creation**  | Financial literacy modules, micro-loan tracking, savings programs           |
| **AI Workflows**     | Claude-powered workflow generation, automated task routing and execution    |
| **Notifications**    | Email, in-app, and SMS notifications via Celery tasks                       |
| **Admin / RBAC**     | Role-based access control, user management, audit logs                      |

## Development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# All tests
make test

# Backend only
make test-backend

# Frontend only
make test-frontend
```

## License

Proprietary. All rights reserved.
