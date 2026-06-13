# MigrantsBridge — Upskilling Roadmap

> You asked: *"Which areas do I need to upskill? Give me all the tools and let me study seriously. No BS, be brutally honest."*
>
> This is that answer. It is grounded in **your actual codebase** — not a generic
> "learn to code" list. Every gap below is something this repo already depends on
> and that you will be on the hook for when it breaks in production.

---

## 0. The brutally honest summary

You (with AI help) have built a platform that is **architecturally ambitious** —
15 backend services, 13 API modules, 5 Celery worker groups, 6 external
integrations (Claude, email, SMS, Stripe-style payments, S3 storage, plus auth),
a Next.js dashboard with RBAC. That is genuinely impressive in scope.

But scope is not the same as **operational maturity**, and that is the gap:

| What exists | What's missing | Risk if ignored |
|---|---|---|
| 15 services with business logic | **0 backend tests** (`backend/tests/` is empty) | Every change is a guess. You can't refactor safely. |
| 13 API route modules | **No CI** (`.github/workflows/` doesn't exist) | Broken code reaches `main` silently. |
| Full DB schema across ~12 models | **Only 2 Alembic migrations** | Schema drift; prod migrations will fail. |
| 6 integrations (payment, SMS, email, storage, Claude) | No idea which are real vs. stubbed | You'll discover failures from angry users, not logs. |
| Async SQLAlchemy + Celery | Unknown if you understand the async/transaction model | Data races, partial writes, "why is it slow" mysteries. |

**The single most important skill to acquire is not a framework — it is the
discipline of testing + CI + observability.** Without it, a codebase this size
becomes unmaintainable by one person within months. Everything else below is
secondary to that. I am putting it first deliberately.

---

## Tier 1 — Non-negotiable (do these first, in order)

These are the skills that stop the project from collapsing under its own weight.

### 1.1 Automated Testing (Python)
**Why for you:** You have 15 services and zero tests. You literally cannot know
if a change broke something. This is the #1 gap.

- **Tools to learn:** `pytest`, `pytest-asyncio`, `httpx.AsyncClient` (for API
  tests), `factory-boy` (test data), `pytest-cov` (coverage), `freezegun`
  (time), `respx` (mock HTTP / mock the Claude + payment + SMS calls).
- **Concepts:** unit vs. integration vs. e2e; fixtures; mocking external
  services; test databases (transactional rollback per test); arrange-act-assert.
- **Study:**
  - "Architecture Patterns with Python" (Percival & Gregory) — free at
    [cosmicpython.com](https://www.cosmicpython.com/). The single best book for
    *your exact stack* (services + repositories + testing).
  - [pytest docs](https://docs.pytest.org/) — read the fixtures + parametrize chapters.
  - Real Python: "Testing FastAPI applications".
- **Concrete first task:** Write tests for `auth_service` and `client_service`.
  Target: every service has at least a happy-path + one failure-path test.

### 1.2 CI/CD
**Why for you:** No `.github/workflows`. Nothing stops a broken commit.

- **Tools:** GitHub Actions (you're already on GitHub), `ruff` (lint+format),
  `mypy` (type checking), `pre-commit` (run checks before commit).
- **Concepts:** pipeline stages, caching deps, matrix builds, branch protection,
  required status checks, secrets management in CI.
- **Study:** [GitHub Actions docs](https://docs.github.com/actions) — quickstart +
  "Building and testing Python" + "Building and testing Node.js".
- **Concrete first task:** A workflow that on every PR runs: backend `ruff` +
  `mypy` + `pytest`, frontend `lint` + `tsc --noEmit` + `test` + `build`. Then
  turn on branch protection requiring it to pass before merge.

### 1.3 Database & Migrations (Alembic + SQLAlchemy 2.0 async)
**Why for you:** A 12-model schema with only 2 migrations means schema changes
aren't being tracked properly. In prod, a bad migration = downtime or data loss.

- **Tools:** Alembic (autogenerate, `upgrade`/`downgrade`, branching/merging),
  SQLAlchemy 2.0 async ORM, `asyncpg`.
- **Concepts:** sessions & the unit-of-work pattern, `async with session.begin()`,
  N+1 queries and `selectinload`/`joinedload`, transactions & rollback,
  connection pooling, indexes, why soft-deletes + UUID PKs have query costs.
- **Study:**
  - [SQLAlchemy 2.0 ORM tutorial](https://docs.sqlalchemy.org/en/20/orm/) — the
    async section specifically.
  - [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html) +
    the "autogenerate" and "branching" cookbook pages.
  - Use [Postgres `EXPLAIN ANALYZE`](https://www.postgresql.org/docs/current/sql-explain.html)
    on your slowest endpoints.
- **Concrete first task:** Add an index migration for the columns your list
  endpoints filter/sort on. Practice `downgrade` to prove rollbacks work.

---

## Tier 2 — Core competency (the day-to-day craft)

### 2.1 FastAPI in depth
You use it everywhere; make sure you actually understand it.
- **Concepts:** dependency injection (`Depends`), the request lifecycle,
  `BackgroundTasks` vs. Celery, middleware (you have a `middleware.py` — know what
  it does), `lifespan` startup/shutdown, response models & `response_model_exclude`,
  proper status codes, exception handlers.
- **Study:** [FastAPI docs](https://fastapi.tiangolo.com/) — read *all* of the
  "Tutorial" and "Advanced" sections. They're excellent. Then "Bigger
  Applications" + "Testing".

### 2.2 Async Python (the thing that will bite you)
Async is where subtle, hard-to-debug bugs live.
- **Concepts:** event loop, `async`/`await`, never block the loop (no sync I/O,
  no `time.sleep`), `asyncio.gather`, cancellation, why a sync DB call in an async
  route stalls everything.
- **Study:** [Real Python — Async IO in Python](https://realpython.com/async-io-python/);
  the [FastAPI "async" explainer](https://fastapi.tiangolo.com/async/).

### 2.3 Celery & background jobs
You have 5 worker modules (documents, notifications, reminders, reporting,
workflows). These fail silently more than anything else.
- **Concepts:** task idempotency, retries with backoff, `acks_late`, visibility
  timeout, beat scheduling, dead-letter handling, monitoring queue depth, why you
  must never pass ORM objects to tasks (pass IDs).
- **Tools:** Celery, Redis (as broker + result backend), **Flower** (monitoring UI).
- **Study:** [Celery docs — "Tasks" and "Periodic Tasks"](https://docs.celeryq.dev/);
  the "Best Practices" section is mandatory reading.

### 2.4 TypeScript + Next.js 14 (App Router)
- **Concepts:** Server vs. Client Components (the #1 App Router confusion), server
  actions, data fetching & caching, route groups (you use `(auth)`/`(portal)`/
  `(dashboard)`), TanStack Query (cache invalidation, optimistic updates), Zustand,
  Zod, why your API types should be generated, not hand-written.
- **Study:** [Next.js Learn course](https://nextjs.org/learn) (official, free);
  [TanStack Query docs](https://tanstack.com/query/latest); the
  [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html).

### 2.5 Git & code review discipline
- **Concepts:** small PRs, meaningful commits, branching strategy, code review,
  resolving conflicts, `bisect` for finding regressions.
- **Study:** [Pro Git book](https://git-scm.com/book) (free). Practice rebasing on
  a throwaway branch until it stops scaring you.

---

## Tier 3 — Production readiness (before real users depend on it)

### 3.1 Observability & logging
**Brutal truth:** right now if something breaks in prod you'll find out from a
user, not a dashboard.
- **Tools:** structured logging (`structlog`), **Sentry** (error tracking — free
  tier, 30 min to set up, enormous payoff), OpenTelemetry, Prometheus + Grafana
  (later), `/health` + readiness probes.
- **Study:** Sentry's FastAPI + Next.js integration guides; "structured logging
  python" — log JSON with request IDs you can grep.

### 3.2 Security (you handle immigration data — this is not optional)
You're processing some of the most sensitive PII that exists. Treat it that way.
- **Concepts:** OWASP Top 10, secrets management (no secrets in git — audit this
  *today*), JWT pitfalls (expiry, rotation, where you store tokens), rate limiting,
  input validation, SQL injection (you're mostly safe via ORM, but know why),
  file-upload security (you accept documents), PII encryption at rest, audit logs,
  least-privilege RBAC.
- **Tools:** `bandit` (Python security linter), `pip-audit` / `npm audit`,
  Dependabot, `trufflehog`/`gitleaks` (secret scanning).
- **Study:** [OWASP Top 10](https://owasp.org/www-project-top-ten/); OWASP
  "Cheat Sheet Series" (Auth, JWT, File Upload, Logging).
- **Concrete first task:** Run `gitleaks` over your whole git history. Then add
  `pip-audit` + `npm audit` to CI.

### 3.3 Docker & deployment
You have `docker-compose.yml` for dev. Prod is a different animal.
- **Concepts:** multi-stage builds, non-root containers, image size, env-based
  config, health checks, where this actually runs (managed Postgres? Redis?
  object storage?), zero-downtime deploys, running migrations on deploy safely.
- **Study:** [Docker docs — best practices](https://docs.docker.com/build/building/best-practices/);
  pick one host (Railway/Render/Fly.io/AWS) and learn it end-to-end.

### 3.4 The Claude / AI integration layer
Your differentiator is AI workflows — so the integration must be robust.
- **Concepts:** retries & timeouts on the API, structured output (tool use / JSON
  mode) instead of regex-parsing prose, token/cost budgeting, prompt versioning,
  evals (how do you know a prompt change didn't make things worse?), guardrails on
  AI-generated workflows before they execute, PII handling in prompts.
- **Study:** [Anthropic docs](https://docs.anthropic.com/) — "Tool use",
  "Prompt engineering", and "Building evals". Use the latest Claude models
  (Opus 4.8 / Sonnet 4.6 / Haiku 4.5) and the `anthropic` SDK's built-in retries.
- **Concrete first task:** Replace any "parse text out of the model response"
  logic with tool-use / structured JSON output, and add a timeout + retry wrapper.

---

## Tier 4 — Architecture & scale (the senior-engineer layer)

Learn these once Tier 1–3 are solid. Don't skip ahead.
- **System design:** caching strategies (Redis), idempotency, rate limiting,
  pagination at scale, the read/write split, eventual consistency.
- **API design:** versioning (you have `/api/v1`), pagination/filtering contracts,
  error envelopes, OpenAPI as the source of truth → generate the frontend types.
- **Data modeling:** normalization vs. read-optimized, when soft-delete hurts,
  multi-tenancy if you ever serve multiple orgs.
- **Study:** "Designing Data-Intensive Applications" (Kleppmann) — the book that
  separates mid from senior. Read it slowly over months.

---

## The tool checklist (print this, tick as you learn)

**Python / Backend**
- [ ] pytest + pytest-asyncio + httpx test client
- [ ] factory-boy, respx (mocking), freezegun
- [ ] ruff (lint+format), mypy (types), bandit (security)
- [ ] Alembic (autogenerate, up/down, branches)
- [ ] SQLAlchemy 2.0 async (eager loading, transactions)
- [ ] Celery best practices + Flower
- [ ] structlog + Sentry

**Frontend**
- [ ] TypeScript (strict mode), generics, utility types
- [ ] Next.js App Router (server vs client components)
- [ ] TanStack Query (cache invalidation)
- [ ] Vitest + React Testing Library + Playwright (e2e)
- [ ] Zod (and generating types from your API)

**Platform / Ops**
- [ ] GitHub Actions (CI) + branch protection
- [ ] pre-commit hooks
- [ ] Docker multi-stage + a real deploy target
- [ ] gitleaks / pip-audit / npm audit / Dependabot
- [ ] Postgres EXPLAIN ANALYZE + indexing

**AI**
- [ ] Anthropic SDK: tool use / structured output, retries, evals
- [ ] Prompt versioning + cost tracking

---

## Suggested 12-week study plan (≈8–10 hrs/week)

| Weeks | Focus | Outcome |
|---|---|---|
| 1–2 | pytest fundamentals → test `auth` + `client` services | First 20 real tests, green |
| 3 | GitHub Actions CI + ruff + mypy + branch protection | No broken code reaches `main` |
| 4–5 | SQLAlchemy async + Alembic deep dive | Confident migrations, fix N+1s |
| 6 | FastAPI advanced + async correctness | Understand DI, lifespan, middleware |
| 7 | Celery best practices + Flower | Idempotent, retrying, monitored tasks |
| 8 | Sentry + structured logging | See errors before users report them |
| 9 | Security audit (OWASP, gitleaks, audits) | PII-handling you can defend |
| 10 | TypeScript + Next.js App Router depth | Stop fighting server/client components |
| 11 | Docker prod + one deploy target | Reproducible, real deployment |
| 12 | Claude tool-use + evals | Robust, testable AI layer |

After week 12, start "Designing Data-Intensive Applications" as ongoing reading.

---

## One rule to live by

> **Don't add a 16th service until the first 15 have tests.**
> Breadth is not the problem here — depth is. Every new feature without tests and
> CI is debt you personally will pay back later, with interest, at 2am.

You have the ambition and the architecture. Now build the engineering discipline
underneath it. Start at Tier 1.1 today.
