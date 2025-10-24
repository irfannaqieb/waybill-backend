from fastapi import APIRouter

mock_router = APIRouter(prefix="/mock")


@mock_router.get("/track/{tracking_id}")
async def track(tracking_id: str):
    return {
        "tracking_id": tracking_id,
        "status": "In Transit",
        "last_scan": "KUL Hub",
        "eta": "2025-10-28",
        "history": [
            {"loc": "Pickup", "ts": "2025-10-23"},
            {"loc": "KUL Hub", "ts": "2025-10-24"},
        ],
    }
