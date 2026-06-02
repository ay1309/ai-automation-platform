from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import chat
from app.routes import rag
from app.routes import health
from app.routes import documents
from app.routes import conversations

from app.db.database import engine
from app.db.models import Base


# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AFMB Talent Assistant API",
    description="FastAPI backend for AFMB Talent Assistant with RAG, document upload, and conversation history.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://afmb-talent-assistant.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# routers
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(documents.router)
app.include_router(conversations.router)
app.include_router(health.router)


@app.get("/")
async def root():
    return {
        "message": "AFMB Talent Assistant API Running",
        "docs": "/docs",
        "health": "/health"
    }