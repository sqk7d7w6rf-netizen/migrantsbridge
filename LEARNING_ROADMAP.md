# MigrantsBridge — Learning Roadmap

> A brutally honest, no-BS upskilling plan **grounded in this exact codebase** — not a generic bootcamp syllabus. Every skill below maps to real files you already own. Work through it top to bottom, check the boxes, and you go from passenger to pilot.

---

## The unvarnished situation

This is what an audit of the repo actually shows. Read it once, then never need to be told again.

- **This is a genuinely advanced app — roughly 7/10 complexity.** ~15k lines of backend code across 114 Python files; ~196 TypeScript/TSX files on the frontend. Async SQLAlchemy 2.0, Celery + Redis task queue, JWT + RBAC auth, Claude API integration, Alembic migrations, a 6-service Docker Compose stack, and Next.js 14 App Router.
- **It was built scaffold-first by AI, then patched.** Git history shows ~54% of commits are "fix" commits — CORS-with-credentials bugs, "fix API mismatch" across modules, a `.gitignore` that *deleted* `frontend/src/lib`, config-parsing crashes, and a missing `email-validator` dependency that broke `app.main` from even importing.
- **Until very recently there were ZERO automated tests and ZERO CI.** A 7/10 system with a 0/10 safety net.

**The metaphor that matters:** you're flying an aircraft you can't yet hand-fly. The autopilot (AI) built it and keeps it level — but you can't read the instruments, you don't know which warning lights are fatal, and you can't land it if the autopilot quits. This roadmap makes you the pilot.

**How the pieces connect (memorize this mental model):**

```
Browser
  │  HTTPS
  ▼
Next.js 14 (frontend :3000)  ──proxy/rewrites──►  FastAPI (backend :8000)
  │  TanStack Query / Axios                          │  Depends() DI, Pydantic
  │  Zustand (client state)                          ▼
  │                                          SQLAlchemy 2.0 (async)
  │                                                  │
  │                                                  ▼
  │                                          PostgreSQL 16  ◄── Alembic migrations
  │                                                  ▲
  │                                                  │
FastAPI ──enqueue──► Redis ──broker──► Celery worker + beat
                                          │  OCR, notifications, workflows
                                          ▼
                                   Claude API (Anthropic)
```

---

## How to use this document

- Each skill has a **checklist box** — tick it when you can *explain it to someone else*, not just nod along.
- Each skill has a **Resources** block: **Docs · Free · Paid · Video · Book**. Pick the medium that fits you; you don't need all of them.
- Follow the **study sequence at the bottom** — order matters. Don't start at Celery.
- Read the **Danger Zone** section before you change anything in those files.

Legend: 📄 official docs · 🆓 free course · 💳 paid course · ▶️ video/YouTube · 📕 book

---

# TIER 0 — Non-negotiable foundations

If a "fix API mismatch" commit confuses you, the gap is here. Do not skip this tier to get to the "fun" stuff. These four pay for themselves in week one.

### - [ ] The command line & Git
**Why it bit you:** a `.gitignore` mistake *deleted* `frontend/src/lib`. That is a Git-literacy gap, full stop. You will use Git every single day.
**Master:** `clone/add/commit/push/pull`, branches, `merge` vs `rebase`, `revert`, **`reflog`** (your undo button), `.gitignore` rules, resolving conflicts, reading a diff.
- 📄 [Git official docs](https://git-scm.com/doc) · [GitHub Docs: Git basics](https://docs.github.com/en/get-started/using-git)
- 🆓 [Pro Git book — free, the definitive reference](https://git-scm.com/book/en/v2) · [freeCodeCamp Git & GitHub course](https://www.freecodecamp.org/news/git-and-github-for-beginners/) · [Atlassian Git tutorials](https://www.atlassian.com/git/tutorials)
- 🆓 Interactive: [Learn Git Branching (visual, gamified)](https://learngitbranching.js.org/) · [GitHub Skills](https://skills.github.com/)
- 💳 [Udemy: Git Complete (Jason Taylor)](https://www.udemy.com/course/git-complete/)
- ▶️ [The Net Ninja — Git & GitHub playlist](https://www.youtube.com/playlist?list=PL4cUxeGkcC9goXbgTDQ0n_4TBzOO0ocPR) · [Fireship — Git in 100 seconds / 13 commands](https://www.youtube.com/watch?v=hwP7WQkmECE)
- 📕 *Pro Git* (Chacon & Straub) — free online above.
- **Command line:** ▶️ [MIT "Missing Semester" — the most useful CS class never taught](https://missing.csail.mit.edu/) · 📕 *The Linux Command Line* by William Shotts (free PDF at [linuxcommand.org](https://linuxcommand.org/tlcl.php)).

### - [ ] HTTP & REST fundamentals
**Why it bit you:** "API mismatch" = the frontend and backend disagreeing on a contract. The CORS-with-credentials bug lived here too.
**Master:** request/response cycle, methods (GET/POST/PUT/PATCH/DELETE), status codes (2xx/4xx/5xx), headers, JSON bodies, query vs path vs body params, **CORS**, what a "REST resource" is.
- 📄 [MDN: HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP) · [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) · [MDN: HTTP status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- 🆓 [freeCodeCamp: APIs & REST](https://www.freecodecamp.org/news/rest-api-tutorial-rest-client-rest-service-and-api-calls-explained-with-code-examples/) · [Postman Learning Center](https://learning.postman.com/)
- ▶️ [Fireship — HTTP in 100s / CORS in 100s](https://www.youtube.com/watch?v=4PHkrL0pIWE) · [ByteByteGo — REST API best practices](https://www.youtube.com/watch?v=_gQaygjm_hg)
- 📕 *HTTP: The Definitive Guide* (O'Reilly) for depth; *RESTful Web APIs* (Richardson) for API design.
- **Practice:** open your app, watch the browser DevTools → Network tab while you click around. Match each request to a route in `backend/app/api/v1/`.

### - [ ] How a web app is wired (your stack end-to-end)
**Why:** you need the mental model in the diagram above to reason about *any* bug.
**Do this, not a course:** open `docker-compose.yml`, list the 6 services, then trace **one feature** — "create a client" — from the React form (`frontend/src/components/features/clients/client-form.tsx`) → service (`frontend/src/services/clients.service.ts`) → API route (`backend/app/api/v1/clients.py`) → service layer (`backend/app/services/`) → model (`backend/app/models/client.py`) → Postgres. Write down every file it touches.
- ▶️ [ByteByteGo — "How web works" series](https://www.youtube.com/c/ByteByteGo) · [Fireship — 100+ web dev concepts](https://www.youtube.com/watch?v=erEgovG9WBs)
- 📕 *Web Application Architecture* concepts — or just the trace above; it's worth more than any video.

### - [ ] Reading code & errors (the skill nobody teaches)
**Why it bit you:** most "fixes" in the history were misread tracebacks fixed by trial and error.
**Master:** reading a **Python traceback bottom-to-top** (the last line is the error, the lines above are the call stack), reading a **TypeScript compiler error**, reading a **browser console error**, and the discipline of *reading the whole message before changing anything*.
- 📄 [Python: Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html) · [TypeScript error reference](https://www.typescriptlang.org/docs/handbook/2/understanding-errors.html)
- 🆓 [Real Python: Understanding tracebacks](https://realpython.com/python-traceback/)
- ▶️ [mCoding — How to read a Python traceback](https://www.youtube.com/watch?v=KuD8h4Sj-uM)

---

# TIER 1 — The backend stack (where the real complexity lives)

This is ~60% of the value in the whole roadmap. Go slow here, especially on async SQLAlchemy.

### - [ ] Python — modern, typed, async
**Where in your repo:** all of `backend/app/`.
**Master:** Python 3.12 syntax, **type hints** (`list[str]`, `X | None`), dataclasses, decorators, context managers (`async with`), and **`async`/`await` + the `asyncio` event loop**. ⚠️ Your Celery workers do a fragile `asyncio.new_event_loop()` bridge (`backend/app/workers/*`) — you cannot debug it without understanding the event loop.
- 📄 [Python official tutorial](https://docs.python.org/3/tutorial/) · [asyncio docs](https://docs.python.org/3/library/asyncio.html) · [typing docs](https://docs.python.org/3/library/typing.html)
- 🆓 [Real Python — async IO walkthrough](https://realpython.com/async-io-python/) · [freeCodeCamp full Python course](https://www.youtube.com/watch?v=rfscVS0vtbw) · [Python type checking guide (Real Python)](https://realpython.com/python-type-checking/)
- 💳 [Talk Python — Async Techniques course](https://training.talkpython.fm/courses/async-in-python-with-threading-and-multiprocessing) · [Udemy — Complete Python Bootcamp (Portilla)](https://www.udemy.com/course/complete-python-bootcamp/)
- ▶️ [ArjanCodes (software-design-quality Python)](https://www.youtube.com/c/ArjanCodes) · [mCoding](https://www.youtube.com/c/mCoding) · [Tech With Tim — asyncio](https://www.youtube.com/watch?v=t5Bo1Je9EmE)
- 📕 *Fluent Python* (Ramalho, 2nd ed) — the serious one · *Python Crash Course* (Matthes) if starting fresh · *Using Asyncio in Python* (Caleb Hattingh).

### - [ ] FastAPI
**Where:** `backend/app/main.py`, `backend/app/api/v1/*` (15 route files), `backend/app/dependencies.py`.
**Master:** path/query/body params, `Depends()` dependency injection, Pydantic request/response models, `APIRouter`, lifespan events, middleware ordering, the auto-generated OpenAPI docs at `/docs`, async endpoints.
- 📄 [FastAPI docs — genuinely excellent, read cover to cover](https://fastapi.tiangolo.com/) · [Full tutorial](https://fastapi.tiangolo.com/tutorial/)
- 🆓 [TestDriven.io — FastAPI + SQLAlchemy guides](https://testdriven.io/blog/topics/fastapi/) · [FastAPI best-practices repo (zhanymkanov)](https://github.com/zhanymkanov/fastapi-best-practices)
- 💳 [TestDriven.io — "FastAPI and Pydantic" / TDD courses](https://testdriven.io/courses/) · [TalkPython — Modern APIs with FastAPI](https://training.talkpython.fm/courses/getting-started-with-fastapi)
- ▶️ [ArjanCodes — FastAPI series](https://www.youtube.com/results?search_query=arjancodes+fastapi) · [freeCodeCamp — FastAPI full course (Sanchez)](https://www.youtube.com/watch?v=0sOvCWFmrtA)
- 📕 *Building Python Web APIs with FastAPI* (Packt) · *FastAPI* (Bill Lubanovic, O'Reilly).

### - [ ] Pydantic v2
**Where:** `backend/app/schemas/*` (13 files), `backend/app/config.py`.
**Master:** `BaseModel`, field types & constraints (`min_length`, `max_length`), validators, `model_config`, **`BaseSettings`** for env-driven config, and your `Create`/`Read`/`Update` schema split convention.
- 📄 [Pydantic v2 docs](https://docs.pydantic.dev/latest/) · [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- 🆓 [Pydantic docs "Why" + migration v1→v2 guide](https://docs.pydantic.dev/latest/migration/)
- ▶️ [ArjanCodes — Pydantic tutorial](https://www.youtube.com/watch?v=502XOB0u8OY) · [Eric Roby — Pydantic crash course](https://www.youtube.com/results?search_query=pydantic+v2+tutorial)

### - [ ] SQLAlchemy 2.0 (async) — ⭐ the single hardest thing in your codebase
**Where:** `backend/app/core/database.py`, `backend/app/models/*` (14 models).
**Master:** `Mapped[]` type annotations + `mapped_column`, `relationship()` and lazy strategies (`selectinload`, `noload`), `AsyncSession` lifecycle, `async_sessionmaker`, **connection pooling** (`pool_size`, `pool_pre_ping`), `expire_on_commit=False`, the unit-of-work / flush / commit model, and avoiding the **N+1 query** trap.
- 📄 [SQLAlchemy 2.0 ORM tutorial](https://docs.sqlalchemy.org/en/20/tutorial/) · [Asyncio extension](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) · [What's new in 2.0](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html)
- 🆓 [ArjanCodes — SQLAlchemy 2.0](https://www.youtube.com/watch?v=aAy-B6KPld8) · [TestDriven.io — FastAPI + async SQLAlchemy](https://testdriven.io/blog/fastapi-sqlmodel/)
- 💳 [TalkPython — "Modeling and Querying with SQLAlchemy" / "SQLAlchemy 2 in Practice"](https://training.talkpython.fm/courses)
- ▶️ [SQLAlchemy author Mike Bayer talks](https://www.youtube.com/results?search_query=sqlalchemy+2.0+async) · [Pretty Printed — SQLAlchemy series](https://www.youtube.com/c/PrettyPrinted)
- 📕 *Essential SQLAlchemy* (O'Reilly) — note it predates 2.0, pair with the docs.

### - [ ] PostgreSQL & SQL
**Where:** the database behind every model.
**Master:** `SELECT`/`JOIN`/`WHERE`/`GROUP BY`, indexes and why they matter, transactions & isolation, `EXPLAIN` (reading a query plan), foreign keys/constraints, and recognizing an N+1 from the DB side.
- 📄 [PostgreSQL official docs/tutorial](https://www.postgresql.org/docs/current/tutorial.html)
- 🆓 [PostgreSQL Tutorial site](https://www.postgresqltutorial.com/) · [Mode SQL Tutorial](https://mode.com/sql-tutorial/) · [SQLBolt (interactive)](https://sqlbolt.com/) · [pgexercises](https://pgexercises.com/)
- 💳 [Udemy — "The Complete SQL Bootcamp" (Portilla)](https://www.udemy.com/course/the-complete-sql-bootcamp/) · [Udemy — "SQL and PostgreSQL: The Complete Developer's Guide" (Stephen Grider)](https://www.udemy.com/course/sql-and-postgresql/)
- ▶️ [freeCodeCamp — PostgreSQL full course](https://www.youtube.com/watch?v=qw--VYLpxG4) · [Hussein Nasser — database engineering](https://www.youtube.com/c/HusseinNasser-software-engineering)
- 📕 *The Art of PostgreSQL* (Dimitri Fontaine) · *SQL Performance Explained* (Markus Winand, also [use-the-index-luke.com](https://use-the-index-luke.com/)).

### - [ ] Alembic migrations — ⚠️ learn before you touch production data
**Where:** `backend/alembic/` (async `env.py`, 2 migrations including a 61KB initial schema).
**Master:** `alembic revision --autogenerate -m "..."`, `alembic upgrade head` / `downgrade`, reviewing autogenerated migrations *before* running them, why your `env.py` is async, and safe migration practice (additive first, never blindly drop columns).
- 📄 [Alembic docs](https://alembic.sqlalchemy.org/en/latest/) · [Autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html) · [Async env recipe](https://alembic.sqlalchemy.org/en/latest/cookbook.html)
- 🆓 [TestDriven.io — Alembic with FastAPI](https://testdriven.io/blog/fastapi-sqlmodel/) · [Real Python — Flask-by-example migrations (concepts transfer)](https://realpython.com/)
- ▶️ [Pretty Printed — Alembic basics](https://www.youtube.com/results?search_query=alembic+sqlalchemy+migrations)

### - [ ] Celery + Redis (async task queue)
**Where:** `backend/app/core/celery_app.py`, `backend/app/workers/*` (6 task files: OCR, notifications, reminders, reporting, workflows).
**Master:** broker vs result backend, defining tasks, `.delay()`/`.apply_async()`, **retries** (`max_retries`, `default_retry_delay`, `self.retry()`), `task_acks_late`, queue routing (you have `default`/`workflows`/`notifications` queues), Celery **beat** scheduling, and the async-in-sync `new_event_loop()` bridge your tasks use.
- 📄 [Celery docs](https://docs.celeryq.dev/en/stable/) · [First steps](https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html) · [Redis docs](https://redis.io/docs/latest/)
- 🆓 [TestDriven.io — "The Definitive Guide to Celery and FastAPI" (free articles)](https://testdriven.io/courses/fastapi-celery/) · [Real Python — async tasks with Celery](https://realpython.com/asynchronous-tasks-with-django-and-celery/)
- 💳 [TestDriven.io — Celery + FastAPI full course](https://testdriven.io/courses/fastapi-celery/)
- ▶️ [Very Academy — Celery series](https://www.youtube.com/results?search_query=very+academy+celery) · [Redis crash courses on freeCodeCamp](https://www.youtube.com/watch?v=jgpVdJB2sKQ)
- 📕 *Redis in Action* (free at [redislabs](https://redis.com/ebook/redis-in-action/)).

### - [ ] Auth — JWT + RBAC + password security
**Where:** `backend/app/core/security.py`, `backend/app/models/user.py` (User/Role/Permission), `backend/app/services/auth_service.py`.
**Master:** what a JWT is (header.payload.signature), access vs refresh tokens, `OAuth2PasswordBearer`, bcrypt password hashing (passlib), token claims, the Role→Permission graph (many-to-many junction), and the `require_permission()` dependency factory. ⚠️ **Security you don't understand is security you don't have** — you shipped a default `SECRET_KEY`.
- 📄 [FastAPI — Security tutorial (OAuth2 + JWT)](https://fastapi.tiangolo.com/tutorial/security/) · [jwt.io — decode & learn](https://jwt.io/) · [OWASP Auth Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- 🆓 [Auth0 — "JWT Handbook" (free PDF)](https://auth0.com/resources/ebooks/jwt-handbook) · [TestDriven.io — FastAPI JWT auth](https://testdriven.io/blog/fastapi-jwt-auth/)
- 🆓 [OWASP Top 10](https://owasp.org/www-project-top-ten/) — read it once, it's short and it matters for client immigration data.
- ▶️ [Web Dev Simplified — JWT explained](https://www.youtube.com/watch?v=7Q17ubqLfaM) · [PyImageSearch/ArjanCodes auth tutorials]
- 📕 *OAuth 2 in Action* (Manning) for the protocol depth.

### - [ ] Claude API / prompt engineering — ⭐ your product's differentiator
**Where:** `backend/app/integrations/claude.py`, `backend/app/services/ai_service.py`, `backend/app/prompts/*` (workflow generation, doc classification, eligibility, task routing).
**Master:** the Anthropic Python SDK (`AsyncAnthropic`), the Messages API, system prompts, **structured/JSON output** and how to *validate* it (⚠️ yours silently `.setdefault()`s malformed JSON — a real risk), temperature & `max_tokens` tuning, handling thinking/tool blocks (don't blind-index `content[0].text`), retries & error handling, and **prompt caching** to cut cost.
- 📄 [Anthropic API docs](https://docs.anthropic.com/) · [Prompt engineering guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) · [Tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use) · [Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- 🆓 [Anthropic Academy / courses (free)](https://www.anthropic.com/learn) · [Anthropic prompt-engineering interactive tutorial (GitHub)](https://github.com/anthropics/courses) · [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)
- 💳 [DeepLearning.AI × Anthropic short courses (mostly free)](https://www.deeplearning.ai/short-courses/)
- ▶️ [Anthropic YouTube channel](https://www.youtube.com/@anthropic-ai) · talks on building with Claude.
- **Model note:** the repo uses `claude-sonnet-4-6` (a deliberate, current choice). When you build new AI features, default to the latest capable Claude models and check current model IDs in the docs above.

---

# TIER 2 — The frontend stack

### - [ ] TypeScript
**Where:** all ~196 `.ts/.tsx` files; strict mode is on (`frontend/tsconfig.json`).
**Master:** types vs interfaces, unions/intersections, **generics** (your `DataTable<TData, TValue>`), `tsc --noEmit`, utility types (`Partial`, `Record`, `Pick`), path aliases (`@/*`), narrowing.
- 📄 [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) · [TS Playground](https://www.typescriptlang.org/play)
- 🆓 [Total TypeScript — free Beginner's Tutorial (Matt Pocock)](https://www.totaltypescript.com/tutorials) · [Type Challenges](https://github.com/type-challenges/type-challenges)
- 💳 [Total TypeScript — Pro (Matt Pocock, the gold standard)](https://www.totaltypescript.com/) · [ExecuteProgram — TypeScript](https://www.executeprogram.com/courses/typescript)
- ▶️ [Matt Pocock YouTube](https://www.youtube.com/@mattpocockuk) · [Fireship — TypeScript in 100s](https://www.youtube.com/watch?v=zQnBQ4tB3ZA)
- 📕 *Programming TypeScript* (Boris Cherny, O'Reilly) · *Effective TypeScript* (Dan Vanderkam).

### - [ ] React 18
**Where:** all of `frontend/src/**`.
**Master:** components & JSX, props, `useState`/`useEffect`/`useMemo`/`useCallback`/`useRef`/`useContext`, the rendering & re-render model, lifting state, controlled inputs, keys, custom hooks. ⚠️ Learn `useMemo` vs `useEffect` carefully — there's a real bug in `kanban-board.tsx` where `useMemo` is misused for a side effect.
- 📄 [react.dev — the new official docs (do the "Learn" path)](https://react.dev/learn)
- 🆓 [Scrimba — Learn React (free)](https://scrimba.com/learn/learnreact) · [freeCodeCamp React](https://www.freecodecamp.org/learn/front-end-development-libraries/)
- 💳 [Epic React (Kent C. Dodds)](https://epicreact.dev/) · [Josh Comeau — "The Joy of React"](https://www.joyofreact.com/) · [Udemy — React (Maximilian Schwarzmüller)](https://www.udemy.com/course/react-the-complete-guide-incl-redux/)
- ▶️ [Web Dev Simplified — React Hooks](https://www.youtube.com/c/WebDevSimplified) · [Jack Herrington](https://www.youtube.com/@jherr)
- 📕 *Learning React* (O'Reilly, 2nd ed).

### - [ ] Next.js 14 App Router — the #1 source of frontend confusion
**Where:** `frontend/src/app/` with route groups `(auth)`, `(portal)`, `(dashboard)`.
**Master:** the App Router file conventions (`layout.tsx`, `page.tsx`, route groups), **Server Components vs Client Components** (`"use client"`), nested layouts, the API rewrites/proxy to the backend, middleware, dynamic routes (`[step]`). Note: your dashboard is almost entirely client-rendered today — understand the tradeoff.
- 📄 [Next.js docs — "Learn" course is interactive & excellent](https://nextjs.org/learn) · [App Router docs](https://nextjs.org/docs/app)
- 🆓 [Official Next.js Learn (free, build-along)](https://nextjs.org/learn) · [Vercel templates to read](https://vercel.com/templates)
- 💳 [ByteGrad — Next.js Professional](https://bytegrad.com/) · [Udemy — Next.js (Maximilian Schwarzmüller)](https://www.udemy.com/course/nextjs-react-the-complete-guide/)
- ▶️ [Vercel YouTube](https://www.youtube.com/@VercelHQ) · [Lee Robinson (Vercel) tutorials](https://www.youtube.com/@leerob) · [Jack Herrington — App Router deep dives](https://www.youtube.com/@jherr)

### - [ ] TanStack Query (server state)
**Where:** `frontend/src/hooks/queries/` (11 hooks), `frontend/src/services/`, `frontend/src/lib/query-keys.ts`.
**Master:** `useQuery`/`useMutation`, **query keys** (you have a hierarchical key factory — best practice), `staleTime`/`gcTime`, `invalidateQueries`, optimistic updates, `useQueryClient`.
- 📄 [TanStack Query docs](https://tanstack.com/query/latest/docs/framework/react/overview)
- 🆓 [TkDodo's blog — "Practical React Query" series (essential reading)](https://tkdodo.eu/blog/practical-react-query) · [official examples](https://tanstack.com/query/latest/docs/framework/react/examples/basic)
- 💳 [ui.dev — "Query.gg" official TanStack Query course](https://query.gg/)
- ▶️ [TanStack Query crash courses (Web Dev Simplified, Cosden Solutions)](https://www.youtube.com/results?search_query=tanstack+query+tutorial)

### - [ ] Zustand (client state)
**Where:** `frontend/src/stores/` (auth store, sidebar store with `persist` middleware).
**Master:** creating a store, selectors, the `persist` middleware (localStorage), when to use Zustand vs React Query (client state vs server state).
- 📄 [Zustand docs](https://zustand.docs.pmnd.rs/)
- 🆓 [Zustand README + recipes](https://github.com/pmndrs/zustand)
- ▶️ [Jack Herrington — Zustand](https://www.youtube.com/watch?v=sqTPGMipjHk) · [Cosden Solutions — Zustand tutorial](https://www.youtube.com/results?search_query=zustand+tutorial)

### - [ ] Zod + React Hook Form (validation)
**Where:** `frontend/src/lib/validations/`, forms via React Hook Form + `@hookform/resolvers`.
**Master:** Zod schemas (`z.object`, `.min`/`.max`, `.email`, optional/nested, `.default`), inferring TS types from schemas, wiring Zod to React Hook Form. ⚠️ Keep these in sync with backend Pydantic — drift here is exactly your "API mismatch" pain.
- 📄 [Zod docs](https://zod.dev/) · [React Hook Form docs](https://react-hook-form.com/)
- 🆓 [React Hook Form + Zod official examples](https://react-hook-form.com/get-started)
- ▶️ [Web Dev Simplified — RHF + Zod](https://www.youtube.com/results?search_query=react+hook+form+zod) · [Cosden Solutions — Zod](https://www.youtube.com/results?search_query=zod+tutorial)

### - [ ] Tailwind CSS + shadcn/ui
**Where:** `frontend/tailwind.config.ts`, `frontend/src/components/ui/` (18 shadcn components built on Radix), `cn()` in `lib/utils.ts`.
**Master:** utility-first CSS, responsive prefixes, dark mode (next-themes), CSS variables theming, `class-variance-authority` variants, `tailwind-merge`, and how shadcn/ui composes Radix primitives.
- 📄 [Tailwind docs](https://tailwindcss.com/docs) · [shadcn/ui docs](https://ui.shadcn.com/docs) · [Radix UI primitives](https://www.radix-ui.com/primitives)
- 🆓 [Tailwind official screencasts](https://www.youtube.com/tailwindlabs) · [shadcn/ui examples](https://ui.shadcn.com/examples)
- 💳 [Tailwind UI (component library by the makers)](https://tailwindui.com/)
- ▶️ [Tailwind Labs YouTube](https://www.youtube.com/@TailwindLabs) · [The Net Ninja — Tailwind](https://www.youtube.com/results?search_query=net+ninja+tailwind)

### - [ ] Supporting frontend libs
- **next-auth v5 (beta)** — session handling. ⚠️ *Beta = breaking changes between releases; pin and read the changelog.* 📄 [Auth.js docs](https://authjs.dev/)
- **Axios** — HTTP client with interceptors (auth token injection, 401 redirect) in `lib/api-client.ts`. 📄 [Axios docs](https://axios-http.com/)
- **Recharts** — dashboard charts. 📄 [Recharts docs](https://recharts.org/) · ▶️ search "Recharts tutorial"
- **dnd-kit** — the Kanban drag-and-drop. 📄 [dnd-kit docs](https://docs.dndkit.com/) · ▶️ [Code with Antonio — dnd-kit](https://www.youtube.com/results?search_query=dnd-kit+tutorial)
- **date-fns** — date formatting. 📄 [date-fns docs](https://date-fns.org/)

---

# TIER 3 — Engineering discipline (the gap that caused 54% fix-commits)

This tier is the **highest-leverage** thing you can learn for stopping the churn. Tests and CI are not optional busywork — they're the autopilot's seatbelt.

### - [ ] Automated testing
**Where:** `backend/tests/` (pytest) and `frontend` (Vitest) — recently introduced; expand them.
**Master:** unit vs integration tests, the AAA pattern (arrange/act/assert), fixtures, **mocking** (especially the Claude API so tests don't call it), `pytest` markers, async tests (`pytest-asyncio`), test factories (`factory-boy`), and on the frontend, component tests with Vitest + Testing Library.
- 📄 [pytest docs](https://docs.pytest.org/) · [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) · [Vitest docs](https://vitest.dev/) · [Testing Library docs](https://testing-library.com/)
- 🆓 [Real Python — Getting started with pytest](https://realpython.com/pytest-python-testing/) · [TestDriven.io — testing FastAPI](https://testdriven.io/blog/fastapi-crud/)
- 💳 [TestDriven.io — Test-Driven Development with FastAPI](https://testdriven.io/courses/tdd-fastapi/)
- ▶️ [ArjanCodes — testing in Python](https://www.youtube.com/results?search_query=arjancodes+pytest) · [mCoding — pytest](https://www.youtube.com/results?search_query=mcoding+pytest)
- 📕 *Python Testing with pytest* (Brian Okken, Pragmatic Bookshelf) — the book to own.

### - [ ] CI/CD (GitHub Actions)
**Where:** `.github/workflows/ci.yml` (recently added — read every line and understand it).
**Master:** what a workflow/job/step is, triggers (`on: push`/`pull_request`), running pytest + lint + build as gates, caching, concurrency cancellation, branch protection rules.
- 📄 [GitHub Actions docs](https://docs.github.com/en/actions) · [Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- 🆓 [GitHub Skills — "Hello GitHub Actions"](https://github.com/skills/hello-github-actions) · [GitHub Actions by example](https://www.actionsbyexample.com/)
- ▶️ [TechWorld with Nana — CI/CD & GitHub Actions](https://www.youtube.com/watch?v=R8_veQiYBjI) · [Fireship — GitHub Actions in 100s](https://www.youtube.com/watch?v=eB0nUzAI7M8)
- 📕 *Learning GitHub Actions* (Brent Laster, O'Reilly).

### - [ ] Debugging
**Master:** `breakpoint()`/`pdb`, IDE debuggers (VS Code launch configs), browser DevTools (Network, Console, React DevTools), structured logging, bisecting a bug with `git bisect`.
- 📄 [Python pdb docs](https://docs.python.org/3/library/pdb.html) · [Chrome DevTools docs](https://developer.chrome.com/docs/devtools/)
- 🆓 [Real Python — Python debugging with pdb](https://realpython.com/python-debugging-pdb/)
- ▶️ [VS Code debugging tutorials](https://code.visualstudio.com/docs/editor/debugging)

### - [ ] Code review & reading diffs
**Why:** you approve AI-generated changes you can't fully evaluate today. The skill is asking "what could this break?" of every diff.
- 🆓 [Google's Code Review Developer Guide (free, excellent)](https://google.github.io/eng-practices/review/) · [Conventional Commits](https://www.conventionalcommits.org/)
- ▶️ Watch experienced devs review PRs on YouTube (search "code review walkthrough").

---

# TIER 4 — Infrastructure & "can I actually ship this?"

Currently the app is **dev-only**. There is no production deployment story. This tier closes that gap.

### - [ ] Docker & Docker Compose
**Where:** `docker-compose.yml` (6 services: postgres, redis, backend, celery-worker, celery-beat, frontend), `Makefile`.
**Master:** images vs containers, Dockerfiles, layers & caching, volumes (you use named volumes for persistence), health checks, `depends_on` with `service_healthy`, env interpolation, `docker compose up/down/logs/exec`.
- 📄 [Docker docs / Get Started](https://docs.docker.com/get-started/) · [Compose docs](https://docs.docker.com/compose/)
- 🆓 [Docker Curriculum (free)](https://docker-curriculum.com/) · [Play with Docker](https://labs.play-with-docker.com/)
- 💳 [Bret Fisher — "Docker Mastery" (Udemy)](https://www.udemy.com/course/docker-mastery/)
- ▶️ [TechWorld with Nana — Docker full course](https://www.youtube.com/watch?v=3c-iBn73dDE) · [Fireship — Docker in 100s](https://www.youtube.com/watch?v=Gjnup-PuquQ)
- 📕 *Docker Deep Dive* (Nigel Poulton).

### - [ ] Environment & secrets management
**Where:** `.env.example` (27 vars). ⚠️ The app crashes on missing `.env` and you shipped a default `SECRET_KEY`.
**Master:** 12-factor config, `.env` files, never committing secrets (`.gitignore`, secret scanning), generating strong secrets, where secrets live in prod (host env vars, a secrets manager).
- 📄 [The Twelve-Factor App — "Config"](https://12factor.net/config) · [GitHub secret scanning](https://docs.github.com/en/code-security/secret-scanning)
- 🆓 [OWASP — Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

### - [ ] Production deployment
**Where:** *missing entirely* — Docker Compose ≠ production.
**Master:** picking a host (start managed: **Render / Railway / Fly.io**; graduate to AWS/GCP later), managed Postgres + Redis, running Alembic migrations safely on deploy, zero-downtime basics, environment promotion (dev→staging→prod).
- 📄 [Render docs](https://render.com/docs) · [Railway docs](https://docs.railway.app/) · [Fly.io docs](https://fly.io/docs/)
- 🆓 [The Twelve-Factor App (read all 12)](https://12factor.net/) · [DigitalOcean tutorials](https://www.digitalocean.com/community/tutorials)
- ▶️ [TechWorld with Nana — DevOps bootcamp](https://www.youtube.com/c/TechWorldwithNana)
- 📕 *The DevOps Handbook* · later, *Designing Data-Intensive Applications* (Kleppmann) for the deep end.

### - [ ] Observability (logging, error tracking, monitoring)
**Where:** *missing* — you have a RequestID middleware but services don't log it; no error tracking; a request can't be traced.
**Master:** structured logging, log levels, error tracking (Sentry), uptime/health monitoring, basic metrics.
- 📄 [Sentry docs (FastAPI + Next.js SDKs)](https://docs.sentry.io/) · [Python logging HOWTO](https://docs.python.org/3/howto/logging.html)
- 🆓 [Sentry free tier — wire it into both apps](https://sentry.io/)
- ▶️ [Hussein Nasser — observability/monitoring](https://www.youtube.com/c/HusseinNasser-software-engineering)

### - [ ] Backups & data safety — ⚠️ legal/ethical, not just technical
**Why:** you store **immigration client data**. There is no backup or recovery plan. A data-loss event here is a compliance and trust catastrophe, not just an outage.
**Master:** automated Postgres backups (`pg_dump` / managed-provider snapshots), tested restores (a backup you've never restored is not a backup), retention, encryption at rest, and a basic awareness of data-protection obligations for sensitive PII.
- 📄 [PostgreSQL backup & restore docs](https://www.postgresql.org/docs/current/backup.html) · [OWASP — data protection](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- 🆓 Your managed DB provider's backup guide (Render/Railway/RDS all document this).

---

# Recommended study sequence

Don't learn it all at once, and **don't start at Celery.** Order:

1. **Weeks 1–3 — Tier 0.** Git, HTTP/REST, command line, reading tracebacks. Trace "create a client" through your own repo end-to-end (see Tier 0).
2. **Weeks 4–9 — Tier 1 core:** Python async → FastAPI → Pydantic → SQLAlchemy 2.0 → PostgreSQL. This is ~60% of the value. Go slow on async SQLAlchemy.
3. **Weeks 10–12 — Tier 3 testing + CI.** Write tests for the code you now understand. Highest leverage for killing the fix-commit churn.
4. **Weeks 13–16 — Tier 2 frontend:** TypeScript → React → Next.js App Router → TanStack Query + Zod → Tailwind/shadcn.
5. **Weeks 17–18 — Tier 1 remainder:** Alembic deep-dive, Celery + Redis, JWT/RBAC, Claude integration.
6. **Weeks 19–20 — Tier 4 infra:** Docker → secrets → a *real* deployment → backups → observability.

*(Timeline assumes serious part-time study. Compress or stretch to fit your life — the order matters more than the calendar.)*

---

# Danger Zone — your code specifically

Read this before you change any of these. They will hurt if you touch them without understanding first.

### Backend
- **Celery async bridge** — `backend/app/workers/*` create a fresh event loop with `asyncio.new_event_loop()` per task. Re-entrancy or shared async state can corrupt loop state. Understand asyncio first.
- **Async Alembic migrations against production** — `backend/alembic/env.py` is async; the initial schema migration is 61KB. **Always review autogenerated migrations and test on a copy before running on prod.** This is how you avoid destroying client data.
- **Default `SECRET_KEY` guard** — the app now refuses to start with the default secret outside DEBUG. Don't "fix" the startup error by re-enabling the default; generate a real secret.
- **Soft-delete inconsistency** — some queries filter `is_deleted == False`, others don't. Reports may silently include deleted records. There's no global filter — check every query.
- **Unvalidated Claude JSON** — ✅ *Fixed.* `backend/app/services/ai_service.py` previously used `.setdefault()` on model output, which **silently masked malformed JSON**. AI responses are now validated through Pydantic schemas in `backend/app/schemas/ai.py` (types enforced, confidence clamped to 0–1, and failures logged/raised instead of masked). The lesson still stands: never trust AI output without validating its shape.
- **Email adapter is sync** — `integrations/email.py` uses blocking `smtplib`; safe from Celery, but never call it directly from a FastAPI endpoint (it blocks the event loop).
- **No API rate limiting beyond login** — only `POST /auth/login` is throttled. Other endpoints (uploads, etc.) are open to abuse.

### Frontend
- **RBAC enforcement** — ✅ *Fixed.* Previously CLAUDE.md described a `<Can>` component and `usePermission` hook that **did not exist**, so the permission matrix in `frontend/src/config/roles.ts` was never checked and every role saw every menu item. Now implemented: `frontend/src/hooks/use-permission.ts` (`usePermission` — derives permissions from `role_name` via `ROLE_PERMISSIONS`), `frontend/src/components/shared/can.tsx` (`<Can>`), and both `app-sidebar.tsx` and `mobile-nav.tsx` filter nav items by permission. Still true and important: **the frontend is a UX layer only — the backend remains the real security boundary.**
- **Module-level mutable state** — `frontend/src/app/(portal)/intake/[step]/page.tsx` stores form data in module-level `let` variables. This is **not SSR-safe** and can leak between requests. Should be a Zustand store.
- **`useMemo` misused as `useEffect`** — `frontend/src/components/features/tasks/kanban-board.tsx` calls `setLocalTasks` inside `useMemo`. That's a side effect in the wrong hook; it can fire inconsistently. Learn the difference (Tier 2 React) before refactoring.
- **No error boundaries** — a single component error crashes the whole page. Add error boundaries once you understand them.
- **No refresh-token rotation** — tokens in localStorage aren't refreshed; expiry just bounces the user to login. Poor UX, and localStorage tokens are XSS-exposed.

### Documentation drift (know this)
**CLAUDE.md has described features that weren't actually implemented** — frontend RBAC enforcement was the prime example (now fixed). The general lesson stands: don't trust the docs as a spec — verify against the code. This kind of drift is a symptom of the scaffold-first build process, and a reminder of why Tier 3 (tests + CI) matters: a test asserting "viewer cannot see the Billing nav item" would have caught the original gap immediately.

---

*Built from a full audit of this repository. Update the checkboxes as you go — and when you can teach a topic to someone else, that's when you tick it.*
