from fastapi import APIRouter
from pathlib import Path
import json
import random

mock_router = APIRouter(prefix="/mock")
mock_file = Path(__file__).with_name("mock_shipments.json")

with open(mock_file, "r", encoding="utf-8") as f:
    MOCK_SHIPMENTS = json.load(f)


@mock_router.get("/track/{tracking_id}")
async def track(tracking_id: str):
    for shipment in MOCK_SHIPMENTS:
        if shipment["tracking_id"].lower() == tracking_id.lower():
            return shipment

    raise HTTPException(
        status_code=404, detail=f"Tracking ID '{tracking_id}' not found"
    )
