from app.guardrails.pii import redact_pii
from app.retrieval.store import DocStore
from app.services.agent import classify_intent, parse_args
from app.services.tools import track_shipment, get_rates, find_locations
from httpx import AsyncClient


async def run_chain(user_message: str, http_client: AsyncClient, llm) -> dict:
    clean = redact_pii(user_message)

    intent = classify_intent(clean)
    args = parse_args(intent, clean)

    tools_used = []
    context_snippets = []
    tool_result = None

    # Execute tools based on intent
    if intent == "track":
        tid = args.get("tracking_id")
        if tid:
            tools_used.append("track_shipment")
            tool_result = track_shipment(tid)
            if not tool_result:
                # Try mock endpoint as fallback
                try:
                    resp = await http_client.get(
                        f"http://localhost:8000/mock/track/{tid}"
                    )
                    if resp.status_code == 200:
                        tool_result = resp.json()
                        tools_used.append("mock.track")
                except:
                    pass
    elif intent == "rates":
        origin = args.get("origin")
        dest = args.get("dest")
        weight = args.get("weight_kg", 1.0)
        if origin and dest:
            tools_used.append("get_rates")
            tool_result = get_rates(origin, dest, weight)
    elif intent == "locations":
        city = args.get("city")
        if city:
            tools_used.append("find_locations")
            tool_result = find_locations(city)

    # Retrieve relevant context from document store
    store = DocStore()
    context_snippets = store.query(clean, k=3)

    # Build system prompt
    sys = (
        "You are a logistics assistant. Be concise, factual, and explain terms briefly. \n"
        "If shipment info is provided, summarize status and ETA clearly. \n"
        "If rates are provided, highlight the best option and explain differences. \n"
        "If locations are provided, list them clearly with addresses. \n"
        "If a tracking ID was searched but not found, explicitly tell the user that the tracking ID does not exist in the system. \n"
        "Cite retrieved document titles inline like [zones], [terms], [policies]. \n"
        "Be friendly and helpful."
    )

    # Format context from documents
    ctx_text = (
        "\n".join([f"[{t}] {d[:300]}" for t, d in context_snippets])
        if context_snippets
        else ""
    )

    # Format tool results
    tool_text = ""
    if tool_result:
        if isinstance(tool_result, list):
            tool_text = f"Tool Results:\n{str(tool_result)}"
        else:
            tool_text = f"Tool Result:\n{str(tool_result)}"
    elif tools_used and intent == "track":
        # Explicitly tell LLM that tracking ID was not found
        tid = args.get("tracking_id")
        tool_text = f"Tracking ID '{tid}' was searched but not found in the system. Inform the user that this tracking ID does not exist."
    elif tools_used and intent == "rates":
        tool_text = "No rates found for the specified origin and destination."
    elif tools_used and intent == "locations":
        tool_text = "No pickup locations found for the specified city."

    # Build the prompt
    prompt_parts = [sys]
    if ctx_text:
        prompt_parts.append(f"\nContext from documents:\n{ctx_text}")
    if tool_text:
        prompt_parts.append(f"\n{tool_text}")
    prompt_parts.append(f"\nUser: {clean}\n\nAnswer:")

    prompt = "\n".join(prompt_parts)

    # Get LLM response
    answer = await llm.complete(prompt)

    # Redact PII from the response
    final = redact_pii(answer)

    return {
        "answer": final,
        "tools_used": tools_used,
        "snippets": [t for t, _ in context_snippets] if context_snippets else [],
        "intent": intent,
        "result": tool_result if tool_result else None,
    }
