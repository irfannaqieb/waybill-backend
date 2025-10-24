from fastapi import HTTPException
from app.guardrails.pii import redact_pii
from app.retrieval.store import DocStore
from httpx import AsyncClient


async def run_chain(user_message: str, http_client: AsyncClient, llm) -> dict:
    clean = redact_pii(user_message)

    intent = "track" if "track" in clean.lower() or "DHL" in clean else "answer"

    tools_used = []
    context_snippets = []

    if intent == "track":
        tools_used.append("mock.track")
        tracking_id = clean.split()[-1] if "DHL" in clean else "DHL12345TEST"
        resp = await http_client.get(f"http://localhost:8000/mock/track/{tracking_id}")
        if resp.status_code != 200:
            raise HTTPException(502, "Upstream mock failed")
        track_json = resp.json()
    else:
        track_json = None

    store = DocStore()
    context_snippets = store.query(clean, k=3)
