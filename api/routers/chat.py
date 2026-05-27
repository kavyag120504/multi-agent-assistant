from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.routers.auth import get_current_user
from agents.orchestrator_agent import run_assistant, clear_memory
from tools.user_memory_db import load_history, clear_history as db_clear_history

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("")
def send_message(req: ChatRequest, user: dict = Depends(get_current_user)):
    user_id = user["id"]
    try:
        response, intent, confidence, agent_runs = run_assistant(req.message, user_id=user_id)
        return {
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "agent_runs": agent_runs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def get_history(user: dict = Depends(get_current_user)):
    history = load_history(user["id"], limit=300)
    return {"history": history}

@router.delete("/history")
def clear_user_history(user: dict = Depends(get_current_user)):
    clear_memory(user["id"]) # Clears cache
    db_clear_history(user["id"]) # Clears DB
    return {"message": "History cleared"}
