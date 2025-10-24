from pydantic import BaseModel
from fastapi import APIRouter
from app.services.agent import run_agent

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(request: ChatRequest):
    response = run_agent(request.message)
    return response
