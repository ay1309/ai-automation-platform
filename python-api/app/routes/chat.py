from fastapi import APIRouter

from app.schemas.chat_schema import (
    ChatRequest
)

from app.services.openai_service import (
    generate_chat_response
)

router = APIRouter()


@router.post("/chat")
async def chat(req: ChatRequest):

    response = generate_chat_response(
        req.message
    )

    return {
        "response": response
    }