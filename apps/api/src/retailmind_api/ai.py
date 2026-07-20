import json
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Protocol

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
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent",
                headers={"x-goog-api-key": self._api_key},
                json={
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": generation_config,
                },
            )
            response.raise_for_status()

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
