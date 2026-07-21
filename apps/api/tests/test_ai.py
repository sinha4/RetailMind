import asyncio

import httpx
import pytest

from retailmind_api.ai import LyzrAdapter
from retailmind_api.config import Settings


def test_lyzr_adapter_invokes_deployed_agent_with_authenticated_v3_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = __import__("json").loads(request.content)
        assert request.headers["x-api-key"] == "lyzr-test-key"
        assert payload["agent_id"] == "agent-123"
        assert payload["user_id"] == "retailmind-test"
        assert payload["session_id"].startswith("retailmind-")
        assert payload["message"] == "Prepare the customer response"
        return httpx.Response(200, json={"response": "Your curated edit is ready."})

    settings = Settings(
        lyzr_api_key="lyzr-test-key",
        lyzr_agent_id="agent-123",
        lyzr_user_id="retailmind-test",
    )
    output = asyncio.run(
        LyzrAdapter(settings, transport=httpx.MockTransport(handler)).generate(
            "Prepare the customer response"
        )
    )

    assert output.text == "Your curated edit is ready."
    assert output.provider == "lyzr-agent"
    assert output.model == "agent-123"


def test_lyzr_adapter_rejects_structured_intent_use() -> None:
    settings = Settings(lyzr_api_key="lyzr-test-key", lyzr_agent_id="agent-123")

    with pytest.raises(ValueError, match="presentation"):
        asyncio.run(LyzrAdapter(settings).generate("prompt", response_schema={"type": "object"}))
