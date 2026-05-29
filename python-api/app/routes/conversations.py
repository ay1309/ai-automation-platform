import json

from fastapi import APIRouter

from app.db.database import SessionLocal
from app.db.models import Conversation

router = APIRouter()


@router.get("/conversations")
async def get_conversations():

    db = SessionLocal()

    conversations = (
        db.query(Conversation)
        .order_by(Conversation.created_at.desc())
        .limit(50)
        .all()
    )

    result = []

    for conv in conversations:

        sources = []

        if conv.sources:
            try:
                sources = json.loads(conv.sources)
            except Exception:
                sources = []

        result.append({
            "id": conv.id,
            "user_message": conv.user_message,
            "ai_response": conv.ai_response,
            "sources": sources,
            "created_at": str(conv.created_at)
        })

    db.close()

    return result