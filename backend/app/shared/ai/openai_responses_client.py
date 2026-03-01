from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import ServiceError
from app.shared.ai.schemas import AISearchOut, LangMode


logger = logging.getLogger(__name__)


class OpenAIResponsesClient:
    def __init__(self) -> None:
        self._base_url = settings.OPENAI_BASE_URL.rstrip("/")
        self._api_key = settings.OPENAI_API_KEY
        self._timeout = settings.AI_SEARCH_TIMEOUT_SECONDS
        self._model = settings.OPENAI_MODEL

    def _schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "answer": {"type": "string"},
                "suggested_query": {"type": ["string", "null"]},
                "category_hint": {
                    "type": "string",
                    "enum": ["vehicle", "materials", "coming_soon", "unknown"],
                },
                "tags": {"type": "array", "items": {"type": "string"}, "maxItems": 6},
            },
            "required": ["answer", "suggested_query", "category_hint", "tags"],
        }

    def _system_prompt(self, language: LangMode) -> str:
        if language == "english":
            return (
                "You are GraminHub AI Search. Be concise and rural-friendly. "
                "Help the user find relevant categories/items (vehicles, building materials, coming soon). "
                "If the user is asking about how to use the app, explain in simple steps. "
                "Return ONLY valid JSON per the given schema."
            )
        return (
            "आप GraminHub AI Search हैं। जवाब छोटा, साफ और गांव-फ्रेंडली रखें। "
            "यूज़र की जरूरत के हिसाब से category/items सुझाएं (वाहन, निर्माण सामग्री, coming soon). "
            "अगर यूज़र app कैसे use करें पूछे तो 2-4 आसान स्टेप्स बताएं। "
            "दिए गए schema के अनुसार केवल valid JSON लौटाएं।"
        )

    async def search(self, *, query: str, language: LangMode) -> AISearchOut:
        if not self._api_key:
            raise ServiceError("AI search is not configured (missing OPENAI_API_KEY).", status_code=503)

        url = f"{self._base_url}/responses"
        headers = {"Authorization": f"Bearer {self._api_key}"}
        body: dict[str, Any] = {
            "model": self._model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": self._system_prompt(language)}],
                },
                {"role": "user", "content": [{"type": "text", "text": query}]},
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "graminhub_ai_search",
                    "strict": True,
                    "schema": self._schema(),
                }
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(url, headers=headers, json=body)
        except httpx.RequestError as exc:
            logger.warning("OpenAI request error: %s", str(exc))
            raise ServiceError("AI service is temporarily unavailable. Try again.", status_code=503) from exc

        if resp.status_code >= 400:
            logger.warning("OpenAI error status=%s body=%s", resp.status_code, resp.text[:500])
            raise ServiceError("AI service returned an error. Try again.", status_code=503)

        data = resp.json()
        output_text = data.get("output_text") or ""
        if not output_text:
            raise ServiceError("AI response was empty. Try again.", status_code=503)

        try:
            payload = json.loads(output_text)
        except json.JSONDecodeError:
            logger.warning("OpenAI output not JSON: %s", output_text[:500])
            raise ServiceError("AI returned an invalid response. Try again.", status_code=503)

        try:
            return AISearchOut(**payload)
        except Exception as exc:
            logger.warning("OpenAI JSON did not match schema: %s payload=%s", str(exc), payload)
            raise ServiceError("AI returned an unexpected response. Try again.", status_code=503) from exc

