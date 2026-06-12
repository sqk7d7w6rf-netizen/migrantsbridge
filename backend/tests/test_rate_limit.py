"""Tests for the Redis-backed rate limiter (with a fake Redis)."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.core import rate_limit
from app.core.rate_limit import RateLimiter, _client_ip


class FakeRedis:
    """Minimal async Redis stand-in supporting incr/expire/ttl."""

    def __init__(self) -> None:
        self.counters: dict[str, int] = {}
        self.expiries: dict[str, int] = {}
        self.fail = False

    async def incr(self, key: str) -> int:
        if self.fail:
            raise RuntimeError("redis down")
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    async def expire(self, key: str, seconds: int) -> None:
        self.expiries[key] = seconds

    async def ttl(self, key: str) -> int:
        return self.expiries.get(key, -1)


class FakeRequest:
    def __init__(self, host: str = "1.2.3.4", forwarded: str | None = None) -> None:
        self.client = type("C", (), {"host": host})()
        self.headers = {}
        if forwarded:
            self.headers["X-Forwarded-For"] = forwarded


@pytest.fixture
def fake_redis(monkeypatch):
    redis = FakeRedis()
    monkeypatch.setattr(rate_limit, "redis_client", redis)
    return redis


def test_client_ip_prefers_forwarded_header():
    req = FakeRequest(host="10.0.0.1", forwarded="203.0.113.5, 10.0.0.1")
    assert _client_ip(req) == "203.0.113.5"


def test_client_ip_falls_back_to_peer():
    assert _client_ip(FakeRequest(host="9.9.9.9")) == "9.9.9.9"


async def test_allows_requests_under_limit(fake_redis):
    limiter = RateLimiter(limit=3, window_seconds=60, namespace="test")
    req = FakeRequest()
    for _ in range(3):
        await limiter(req)  # should not raise


async def test_blocks_requests_over_limit(fake_redis):
    limiter = RateLimiter(limit=2, window_seconds=60, namespace="test")
    req = FakeRequest()
    await limiter(req)
    await limiter(req)
    with pytest.raises(HTTPException) as exc:
        await limiter(req)
    assert exc.value.status_code == 429
    assert "Retry-After" in exc.value.headers


async def test_sets_expiry_on_first_hit(fake_redis):
    limiter = RateLimiter(limit=5, window_seconds=90, namespace="test")
    await limiter(FakeRequest())
    assert any(v == 90 for v in fake_redis.expiries.values())


async def test_separate_ips_have_separate_budgets(fake_redis):
    limiter = RateLimiter(limit=1, window_seconds=60, namespace="test")
    await limiter(FakeRequest(host="1.1.1.1"))
    # Different IP, fresh budget — should not raise.
    await limiter(FakeRequest(host="2.2.2.2"))


async def test_fails_open_when_redis_unavailable(fake_redis):
    fake_redis.fail = True
    limiter = RateLimiter(limit=1, window_seconds=60, namespace="test")
    # Redis errors must not block the request.
    await limiter(FakeRequest())
    await limiter(FakeRequest())
