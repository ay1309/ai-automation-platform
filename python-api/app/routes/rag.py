import json

from fastapi import APIRouter

from app.schemas.chat_schema import ChatRequest

from app.services.rag_service import (
    ingest_documents,
    ask_rag
)

from app.db.database import SessionLocal
from app.db.models import Conversation

from app.services.rag_service import reset_knowledge_base

router = APIRouter()


@router.post("/ingest")
async def ingest():

    return ingest_documents()


@router.post("/ask")
async def ask(req: ChatRequest):

    result = ask_rag(req.message)

    db = SessionLocal()

    conversation = Conversation(
        user_message=req.message,
        ai_response=result["answer"],
        sources=json.dumps(result["sources"])
    )

    db.add(conversation)

    db.commit()

    db.close()

    return result

@router.post("/reindex")
async def reindex():

    return reset_knowledge_base()

