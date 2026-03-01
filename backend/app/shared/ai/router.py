from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import APIRouter, Request

from app.core.config import settings
from app.core.exceptions import NotFoundError, TooManyRequestsError, ValidationError
from app.shared.ai.openai_responses_client import OpenAIResponsesClient
from app.shared.ai.schemas import AISearchIn, AISearchOut


router = APIRouter(prefix="/api/v2/ai", tags=["v2-ai"])

ai_rate_buckets: dict[str, deque[float]] = defaultdict(deque)


def _host_allowed(host: str, allowed_hosts_csv: str) -> bool:
    host = (host or "").split(":")[0].strip().lower()
    allowed = [h.strip().lower() for h in (allowed_hosts_csv or "").split(",") if h.strip()]
    if not allowed:
        return True
    for pattern in allowed:
        if pattern == host:
            return True
        if pattern.startswith("*.") and host.endswith(pattern[1:]):
            return True
    return False


def _enforce_ai_rate_limit(request: Request) -> None:
    now = time.time()
    ip = request.client.host if request.client else "unknown"
    bucket = ai_rate_buckets[ip]
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= settings.AI_SEARCH_RATE_LIMIT_PER_MINUTE:
        raise TooManyRequestsError("AI search rate limit exceeded. Please wait and try again.")
    bucket.append(now)


@router.post("/search", response_model=AISearchOut)
async def ai_search(payload: AISearchIn, request: Request) -> AISearchOut:
    if not settings.AI_SEARCH_ENABLED:
        raise NotFoundError("Not found")

    if not _host_allowed(request.headers.get("host", ""), settings.AI_SEARCH_ALLOWED_HOSTS):
        raise NotFoundError("Not found")

    query = (payload.query or "").strip()
    if not query:
        raise ValidationError("Query is required.")
    if len(query) > settings.AI_SEARCH_MAX_QUERY_CHARS:
        raise ValidationError("Query is too long.")

    _enforce_ai_rate_limit(request)

    language = payload.language or ("english" if request.headers.get("accept-language", "").lower().startswith("en") else "hindi")
    client = OpenAIResponsesClient()
    return await client.search(query=query, language=language)

