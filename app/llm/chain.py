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

    sys = (
        "You are a logistics assistant. Be concise, factual, and explain terms briefly. \n"
        "If shipment info is provided, summarize status and ETA. \n"
        "Cite retrieved titles inline like [zones], [terms]."
    )
    ctx_text = "\n".join([f"[{t}] {d[:300]}" for t, d in context_snippets])
    ship_text = f"Shipment: {track_json}" if track_json else ""
    prompt = f"{sys}\n\nContext:\n{ctx_text}\n\nUser: {clean}\n{ship_text}\n\nAnswer:"

    answer = await llm.complete(prompt)

    final = redact(answer)
    return {
        "answer": final,
        "tools_used": tools_used,
        "snippets": [t for t, _ in context_snippets],
    }
