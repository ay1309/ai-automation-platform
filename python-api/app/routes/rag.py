from fastapi import APIRouter

from app.schemas.chat_schema import (
    ChatRequest
)

from app.services.rag_service import (
    ingest_documents,
    ask_rag
)

router = APIRouter()


@router.post("/ingest")
async def ingest():

    return ingest_documents()


@router.post("/ask")
async def ask(req: ChatRequest):

    return ask_rag(req.message)