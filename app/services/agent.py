from __future__ import annotations
import re
from typing import Any, Dict, Literal

from app.services.tools import track_shipment, get_rates, find_locations

Intent = Literal["track", "rates", "locations", "unknown"]


def classify_intent(message: str) -> Intent:
    m = message.lower()
    if "track" in m or re.search(r"\b(1z|abc)\w+", m):
        return "track"
    if "rate" in m or "price" in m or ("from" in m and "to" in m):
        return "rates"
    if "location" in m or "pickup" in m or "nearest" in m:
        return "locations"
    return "unknown"


def parse_args(intent: Intent, message: str) -> Dict[str, Any]:
    if intent == "track":
        tid = None
        # Common words to exclude
        exclude_words = {
            "track",
            "tracking",
            "status",
            "package",
            "parcel",
            "shipment",
            "please",
            "check",
            "find",
            "show",
            "what",
            "where",
            "when",
        }

        # First try to find patterns that look like tracking IDs:
        # - Mix of letters and numbers (e.g., "1Z12345", "ABC999")
        # - At least one digit and one letter
        patterns = [
            r"\b([A-Z]{2,}\d{2,}[A-Z0-9]*)\b",  # ABC123, ABC999
            r"\b(\d{1,}[A-Z]{2,}\d{2,})\b",  # 1Z12345
            r"\b([A-Z]\d{4,}[A-Z0-9]*)\b",  # A12345
        ]

        for pattern in patterns:
            m = re.search(pattern, message, re.I)
            if m:
                tid = m.group(1).upper()
                if tid.lower() not in exclude_words:
                    return {"tracking_id": tid}

        # Fallback: find any alphanumeric string 5+ chars, but exclude common words
        all_matches = re.findall(r"\b([A-Za-z0-9]{5,})\b", message)
        for match in all_matches:
            if match.lower() not in exclude_words:
                tid = match.upper()
                return {"tracking_id": tid}

        return {}
    if intent == "rates":
        o = re.search(r"from\s+([A-Za-z\s]+)\s+to\s+([A-Za-z\s]+)", message, re.I)
        w = re.search(r"(\d+(?:\.\d+)?)\s?kg", message, re.I)
        origin = o.group(1).strip() if o else None
        dest = o.group(2).strip() if o else None
        weight = float(w.group(1)) if w else 1.0
        return {"origin": origin, "dest": dest, "weight_kg": weight}

    if intent == "locations":
        c = re.search(r"in\s+([A-Za-z\s]+)$", message.strip(), re.I)
        city = c.group(1).strip() if c else None
        # fallback: look for a known city token
        if city is None:
            for guess in ["Seoul", "Cyberjaya", "Prague", "Kuala Lumpur"]:
                if guess.lower() in message.lower():
                    city = guess
        return {"city": city}

    return {}


def run_agent(message: str) -> str:
    intent = classify_intent(message)
    args = parse_args(intent, message)

    if intent == "track":
        tid = args.get("tracking_id")
        if not tid:
            return {
                "intent": intent,
                "answer": "Please provide a valid tracking ID.",
                "ok": False,
            }
        res = track_shipment(tid)
        if not res:
            return {
                "intent": intent,
                "answer": f"Tracking ID {tid} not found.",
                "ok": False,
            }
        eta = res["eta_days"]
        answer = f"Status: {res['status']}. Last scan: {res['last_scan']}. Estimated arrival: {eta} days."
        return {
            "intent": intent,
            "tool": "track_shipment",
            "*args": {"tracking_id": tid},
            "result": res,
            "answer": answer,
            "ok": True,
        }

    if intent == "rates":
        origin, dest, weight = (
            args.get("origin"),
            args.get("dest"),
            args.get("weight_kg", 1.0),
        )

        if not origin or not dest:
            return {
                "intent": intent,
                "answer": "Please provide a valid origin and destination.",
                "ok": False,
            }
        quotes = get_rates(origin, dest, weight)
        if not quotes:
            return {
                "intent": intent,
                "answer": "No rates found for the given origin and destination.",
                "ok": False,
            }
        best = min(quotes, key=lambda x: x["quote_usd"])
        answer = f"Best rate {best['service']}: ${best['quote_usd']} for {weight}kg, ~{best['transit_days']} day(s)."
        return {
            "intent": intent,
            "tool": "get_rates",
            "args": {"origin": origin, "dest": dest, "weight_kg": weight},
            "result": quotes,
            "answer": answer,
            "ok": True,
        }

    if intent == "locations":
        city = args.get("city")
        if not city:
            return {
                "intent": intent,
                "answer": "Please provide a valid city. E.g., 'Nearest pickup location in Seoul'",
                "ok": False,
            }
        locs = find_locations(city)
        if not locs:
            return {
                "intent": intent,
                "answer": f"No pickup locations found in {city}.",
                "ok": False,
            }
        names = ", ".join(loc["name"] for loc in locs)
        answer = f"Pickup points in {city}: {names}."
        return {
            "intent": intent,
            "tool": "find_locations",
            "args": {"city": city},
            "result": locs,
            "answer": answer,
            "ok": True,
        }

    return {
        "intent": intent,
        "answer": "I can help you with tracking, rates, and pickup locations. Try: 'track 1Z12345' or 'rates from Seoul to Prague 2kg'.",
        "ok": False,
    }
