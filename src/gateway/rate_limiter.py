"""Token-bucket rate limiter as a FastAPI dependency."""

import time
from dataclasses import dataclass, field

from fastapi import HTTPException, Request

from src.config import RATE_LIMIT_CAPACITY, RATE_LIMIT_REFILL_RATE


@dataclass
class TokenBucket:
    capacity: int
    refill_rate: float
    tokens: float = field(init=False)
    last_refill: float = field(init=False)

    def __post_init__(self):
        self.tokens = float(self.capacity)
        self.last_refill = time.monotonic()

    def consume(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class RateLimiter:
    def __init__(
        self,
        capacity: int = RATE_LIMIT_CAPACITY,
        refill_rate: float = RATE_LIMIT_REFILL_RATE,
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets: dict[str, TokenBucket] = {}

    async def __call__(self, request: Request):
        client_ip = request.client.host if request.client else "unknown"
        if client_ip not in self._buckets:
            self._buckets[client_ip] = TokenBucket(
                capacity=self.capacity, refill_rate=self.refill_rate
            )
        if not self._buckets[client_ip].consume():
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
