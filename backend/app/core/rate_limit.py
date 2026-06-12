"""Redis-backed fixed-window rate limiting.

Used to throttle abuse-prone endpoints (most importantly login, to slow down
credential-stuffing and brute-force attacks). The limiter fails open: if Redis
is unavailable the request is allowed through, since availability of the app is
preferred over hard-failing auth when the cache is down.
"""

from __future__ import annotations

import logging

from fastapi import HTTPException, Request, status

from app.core.redis import redis_client

logger = logging.getLogger("migrantsbridge")


def _client_ip(request: Request) -> str:
    """Best-effort client IP, honoring a single proxy hop via X-Forwarded-For."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # First entry is the originating client.
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


class RateLimiter:
    """FastAPI dependency that enforces ``limit`` requests per ``window_seconds``.

    Keys are scoped by ``namespace`` plus the caller's IP, so different endpoints
    don't share a budget.
    """

    def __init__(self, *, limit: int, window_seconds: int, namespace: str) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.namespace = namespace

    async def __call__(self, request: Request) -> None:
        key = f"ratelimit:{self.namespace}:{_client_ip(request)}"
        try:
            current = await redis_client.incr(key)
            if current == 1:
                # First hit in this window — start the expiry clock.
                await redis_client.expire(key, self.window_seconds)
        except Exception:  # noqa: BLE001 - fail open on any Redis error
            logger.warning("Rate limiter unavailable; allowing request", exc_info=True)
            return

        if current > self.limit:
            retry_after = await self._retry_after(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )

    async def _retry_after(self, key: str) -> int:
        try:
            ttl = await redis_client.ttl(key)
        except Exception:  # noqa: BLE001
            ttl = -1
        return ttl if ttl and ttl > 0 else self.window_seconds


# Login: 5 attempts per minute per IP.
login_rate_limiter = RateLimiter(limit=5, window_seconds=60, namespace="login")
