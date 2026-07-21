"""Provider-neutral model protocol and Gemini HTTP adapter."""

import asyncio
import json
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Protocol
from uuid import uuid4

import httpx

from retailmind_api.config import Settings


@dataclass(frozen=True)
class ModelOutput:
    text: str
    latency_ms: int
    provider: str
    model: str


class ModelAdapter(Protocol):
    async def generate(
        self, prompt: str, *, response_schema: dict[str, Any] | None = None
    ) -> ModelOutput: ...


class GeminiAdapter:
    provider = "google-gemini"

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.gemini_api_key or settings.google_api_key
        self._model = settings.gemini_model
        self._timeout = settings.ai_timeout_seconds

    async def generate(
        self, prompt: str, *, response_schema: dict[str, Any] | None = None
    ) -> ModelOutput:
        if not self._api_key:
            raise RuntimeError("Gemini API key is not configured")

        generation_config: dict[str, Any] = {"temperature": 0.2}
        if response_schema:
            generation_config.update(
                responseMimeType="application/json",
                responseSchema=response_schema,
            )

        started = perf_counter()
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for attempt in range(3):
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent",
                    headers={"x-goog-api-key": self._api_key},
                    json={
                        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                        "generationConfig": generation_config,
                    },
                )
                if response.status_code not in {429, 500, 502, 503, 504} or attempt == 2:
                    response.raise_for_status()
                    break
                await asyncio.sleep(0.25 * (attempt + 1))

        payload = response.json()
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        return ModelOutput(
            text=text.strip(),
            latency_ms=round((perf_counter() - started) * 1000),
            provider=self.provider,
            model=self._model,
        )


def parse_json_output(output: ModelOutput) -> dict[str, Any]:
    return json.loads(output.text)


class LyzrAdapter:
    """Invoke a deployed Lyzr Studio v3 agent through the official chat API."""

    provider = "lyzr-agent"

    def __init__(
        self, settings: Settings, *, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._api_key = settings.lyzr_api_key
        self._agent_id = settings.lyzr_agent_id
        self._api_url = settings.lyzr_api_url
        self._user_id = settings.lyzr_user_id
        self._timeout = settings.ai_timeout_seconds
        self._transport = transport

    async def generate(
        self, prompt: str, *, response_schema: dict[str, Any] | None = None
    ) -> ModelOutput:
        if not self._api_key or not self._agent_id:
            raise RuntimeError("Lyzr API key and deployed agent ID are required")
        if response_schema:
            raise ValueError(
                "This Lyzr agent is configured for presentation, not structured intent"
            )

        started = perf_counter()
        async with httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client:
            response = await client.post(
                self._api_url,
                headers={"x-api-key": self._api_key, "Content-Type": "application/json"},
                json={
                    "user_id": self._user_id,
                    "agent_id": self._agent_id,
                    "session_id": f"retailmind-{uuid4()}",
                    "message": prompt,
                    "system_prompt_variables": {},
                    "filter_variables": {},
                    "features": [],
                },
            )
            response.raise_for_status()

        text = response.json()["response"]
        if not isinstance(text, str):
            raise ValueError("Lyzr response did not contain text")
        return ModelOutput(
            text=text.strip(),
            latency_ms=round((perf_counter() - started) * 1000),
            provider=self.provider,
            model=self._agent_id,
        )
