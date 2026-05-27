from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="KAVI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "KAVI API is running"}

from api.routers import auth, chat, todos, insights, workflows

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(todos.router, prefix="/api/todos", tags=["todos"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
