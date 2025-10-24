from fastapi import FastAPI
from app.router_chat import chat_router
from app.mock.router_mock import mock_router
from app.retrieval.ingest import ingest_docs

app = FastAPI()


@app.on_event("startup")
async def startup():
    ingest_docs()


app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(mock_router, tags=["mock"])


@app.get("/health")
async def health():
    return {"ok": True}
