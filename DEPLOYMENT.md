# Deploying MigrantsBridge

## 1. Configure environment

Copy `.env.example` to `.env` and set real values. The ones that matter:

| Variable | What to set |
|---|---|
| `ANTHROPIC_API_KEY` | A real key from https://console.anthropic.com — AI features (workflow generation, document classification, eligibility) raise a clear error until this is set |
| `SECRET_KEY` | A long random string (`openssl rand -hex 32`) |
| `POSTGRES_PASSWORD` / `DATABASE_URL` | Real database credentials |
| `FIRST_ADMIN_EMAIL` / `FIRST_ADMIN_PASSWORD` | Login for the first admin account, created by the seed step |
| `CORS_ORIGINS` | JSON array of allowed browser origins, e.g. `["https://app.example.org"]` — only needed if the frontend calls the backend directly instead of via the built-in proxy |

`NEXT_PUBLIC_API_URL` should stay `/api/v1` (the default): the frontend
proxies API calls to the backend via Next.js rewrites, so browsers and
mobile devices only ever need to reach the frontend's URL. Set
`BACKEND_INTERNAL_URL` to the backend's server-to-server address
(`http://backend:8000` under docker compose — already configured).

## 2. Start the stack

```bash
docker compose up -d --build
```

This starts Postgres, Redis, the API, both Celery workers, and the frontend.

## 3. Migrate and seed (first deploy and after upgrades)

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.initial_data   # idempotent
```

## 4. Verify

```bash
curl http://<host>:8000/health        # backend: {"status":"healthy",...}
curl -I http://<host>:3000            # frontend: 200
```

Log in at `http://<host>:3000/login` with `FIRST_ADMIN_EMAIL` /
`FIRST_ADMIN_PASSWORD`.

## Notes

- Point any client (including mobile) at the **frontend** URL only; the
  backend never needs to be publicly exposed.
- CI (`.github/workflows/ci.yml`) runs migrations, seeds, boots the API
  with smoke tests, and builds the frontend on every PR.
