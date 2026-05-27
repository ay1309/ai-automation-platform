from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker

import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# databese setup
DATABASE_URL = "postgresql://admin:password@postgres:5432/automation"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# model
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text)
    ai_response = Column(Text)

# tables
Base.metadata.create_all(bind=engine)

# openAI appi this time
client = OpenAI(api_key=OPENAI_API_KEY)

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

# cht endpoint
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

    # database save
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