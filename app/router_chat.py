from fastapi import APIRouter
from pydantic import BaseModel
from httpx import AsyncClient
from app.llm.client import LLMClient
from app.llm.chain import run_chain

chat_router = APIRouter()


class ChatIn(BaseModel):
    message: str


@chat_router.post("/")
async def chat(inp: ChatIn):
    async with AsyncClient(timeout=10) as http_client:
        llm = LLMClient()
        result = await run_chain(inp.message, http_client, llm)
    return result
