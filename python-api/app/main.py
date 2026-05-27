import os

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.services.rag_service import (
    process_pdf,
    search_documents
)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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

# root endpoint
@app.get("/")
async def root():
    return {
        "status": "running"
    }

# upload PDF endpoint
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    os.makedirs("/app/documents", exist_ok=True)

    file_location = f"/app/documents/{file.filename}"

    with open(file_location, "wb") as f:
        f.write(await file.read())

    chunks = process_pdf(file_location)

    return {
        "message": "PDF processed successfully",
        "chunks_created": chunks
    }

# ingest all documents endpoint
@app.post("/ingest")
async def ingest_documents():

    documents_path = "/app/documents"

    if not os.path.exists(documents_path):
        return {
            "error": "documents folder not found"
        }

    processed = 0

    for filename in os.listdir(documents_path):

        if filename.endswith(".pdf"):

            file_path = os.path.join(
                documents_path,
                filename
            )

            process_pdf(file_path)

            processed += 1

    return {
        "message": "documents ingested successfully",
        "files_processed": processed
    }

# chat endpoint with RAG
@app.post("/chat")
async def chat(req: ChatRequest):

    retrieved_docs = search_documents(req.message)

    context = "\n\n".join(retrieved_docs)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
You are a professional AI assistant.

Use the following context to answer the user question.

Context:
{context}
"""
            },
            {
                "role": "user",
                "content": req.message
            }
        ]
    )

    ai_response = response.choices[0].message.content

    # save conversation
    db = SessionLocal()

    conversation = Conversation(
        user_message=req.message,
        ai_response=ai_response
    )

    db.add(conversation)

    db.commit()

    db.close()

    return {
        "response": ai_response,
        "context_used": retrieved_docs
    }

@app.get("/health")    # "/health" ckeck endpoint for monitoring
async def health():
    return {
        "status": "healthy"
    }