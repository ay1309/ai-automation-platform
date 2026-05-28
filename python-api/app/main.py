from fastapi import FastAPI

from app.routes import chat
from app.routes import rag
from app.routes import health

from app.db.database import engine
from app.db.models import Base

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Automation Platform"
)

# routers
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(health.router)
