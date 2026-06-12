import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.database import engine
from app.core.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.core.redis import close_redis, redis_client
from app.core.security import validate_production_security
from app.api.router import api_router
from app.exceptions import AppException, app_exception_handler, generic_exception_handler

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("migrantsbridge")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.APP_NAME)
    # Refuse to start with an insecure secret outside DEBUG (raises in production).
    validate_production_security()
    # Verify connectivity but do not crash on failure: requests that need the
    # DB/Redis will error individually, while /health and reconnection
    # (pool_pre_ping) keep working once the dependency comes back.
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda c: None)
        logger.info("Database connection verified")
    except Exception:
        logger.exception("Database unreachable at startup; continuing — will retry per-request")
    try:
        await redis_client.ping()
        logger.info("Redis connection verified")
    except Exception:
        logger.exception("Redis unreachable at startup; continuing — will retry per-request")
    yield
    # Shutdown
    await close_redis()
    await engine.dispose()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Middleware (order matters: first added = outermost)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # API routes
    app.include_router(api_router)

    # Health check
    @app.get("/health", tags=["health"])
    async def health_check():
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": "0.1.0",
        }

    return app


app = create_app()
