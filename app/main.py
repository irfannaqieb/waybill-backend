from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers.chat import router as chat_router
from app.mock.router_mock import mock_router
from app.retrieval.ingest import ingest_docs
import os

app = FastAPI()


@app.on_event("startup")
async def startup():
    ingest_docs()


# Serve static files (if directory exists)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# Serve HTML at root
@app.get("/")
async def root():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Welcome to Waybill API. Visit /docs for API documentation."}


app.include_router(chat_router, prefix="", tags=["chat"])
app.include_router(mock_router, tags=["mock"])


@app.get("/health")
async def health():
    return {"ok": True}
