import pytest
from httpx import AsyncClient
from types import SimpleNamespace
from app.llm.chain import run_chain


class DummyLLM:
    async def complete(self, prompt: str) -> str:
        return "OK [zones] [terms]"


class DummyHTTP:
    # mimic httpx.AsyncClient.get()
    async def get(self, url: str):
        return SimpleNamespace(
            status_code=200,
            json=lambda: {"tracking_id": "DHL123", "status": "In Transit"},
        )


@pytest.mark.asyncio
async def test_run_chain_track():
    llm = DummyLLM()
    http_client = DummyHTTP()
    result = await run_chain("track DHL123 please", http_client, llm)
    assert "mock.track" in result["tools_used"]
    assert isinstance(result["snippets"], list)
    assert "answer" in result and isinstance(result["answer"], str)
