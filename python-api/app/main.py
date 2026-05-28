import os

from dotenv import load_dotenv

from fastapi import FastAPI
from pydantic import BaseModel

from openai import OpenAI

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Text
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)

from app.services.rag_service import (
    ingest_documents,
    ask_rag
)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# database setup
DATABASE_URL = "postgresql://admin:password@postgres:5432/automation"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# database model
class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    user_message = Column(Text)

    ai_response = Column(Text)


# create tables
Base.metadata.create_all(bind=engine)

# fastapi app
app = FastAPI()


# request model
class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def root():

    return {
        "status": "running"
    }


@app.post("/chat")
async def chat(req: ChatRequest):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a professional AI assistant."
            },
            {
                "role": "user",
                "content": req.message
            }
        ]
    )

    ai_response = response.choices[0].message.content

    db = SessionLocal()

    conversation = Conversation(
        user_message=req.message,
        ai_response=ai_response
    )

    db.add(conversation)

    db.commit()

    db.close()

    return {
        "response": ai_response
    }


@app.post("/ingest")
async def ingest():

    try:

        chunks = ingest_documents()

        return {
            "message": "Documents ingested successfully",
            "chunks": chunks
        }

    except Exception as e:

        return {
            "error": str(e)
        }


@app.post("/ask")
async def ask(req: ChatRequest):

    try:

        result = ask_rag(req.message)

        db = SessionLocal()

        conversation = Conversation(
            user_message=req.message,
            ai_response=result["answer"]
        )

        db.add(conversation)

        db.commit()

        db.close()

        return {
            "response": result["answer"],
            "sources": result["sources"]
        }

    except Exception as e:

        return {
            "error": str(e)
        }


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }