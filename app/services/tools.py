from __future__ import annotations
import json

from typing import Any, Dict, List, Optional
from app.config import DATA_PATH

with open(DATA_PATH, "r", encoding="utf-8") as f:
    _DB = json.load(f)


def track_shipment(tracking_id: str) -> Optional[Dict[str, Any]]:
    for s in _DB["shipments"]:
        if s["tracking_id"].lower() == tracking_id.lower():
            return s
    return None


def get_rates(
    origin: str, destination: str, weight_kg: float
) -> Optional[Dict[str, Any]]:
    factor = 1.0 + max(0.0, (weight_kg - 1.0)) * 0.15
    results = []
    for r in _DB["rates"]:
        if (
            r["origin"].lower() == origin.lower()
            and r["destination"].lower() == destination.lower()
        ):
            priced = dict(r)
            priced["quote_usd"] = round(r["price_usd"] * factor, 2)
            priced["weight_kg"] = weight_kg
            results.append(priced)
    return results


def find_locations(city: str) -> List[Dict[str, Any]]:
    return [loc for loc in _DB["locations"] if loc["city"].lower() == city.lower()]
