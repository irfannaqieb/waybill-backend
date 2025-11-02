from pydantic import BaseModel
from fastapi import APIRouter
from httpx import AsyncClient
from app.llm.client import LLMClient
from app.llm.chain import run_chain

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(request: ChatRequest):
    async with AsyncClient(timeout=10) as http_client:
        llm = LLMClient()
        result = await run_chain(request.message, http_client, llm)
    return result
