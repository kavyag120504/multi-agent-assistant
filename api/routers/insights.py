from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.routers.auth import get_current_user
from tools.insights_db import get_insights, dismiss_insight, add_insight
from tools.todo_db import get_tasks
from tools.llm_client import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

router = APIRouter()

@router.get("")
def list_insights(user: dict = Depends(get_current_user)):
    # In a real background worker, insights are pre-generated.
    # For Vercel Serverless, we do a lightweight generation on demand if none exist recently.
    
    existing = get_insights(user["id"], include_dismissed=False)
    
    # Simple logic: if fewer than 2 insights, generate one based on todos
    if len(existing) < 2:
        todos = get_tasks("pending", user["id"])
        if len(todos) > 3:
            add_insight(
                user_id=user["id"],
                title="High Task Volume",
                description=f"You have {len(todos)} pending tasks. Consider prioritizing or delegating some.",
                type="productivity",
                priority="high",
                suggested_action="Review Tasks",
                source_agents="todo"
            )
            existing = get_insights(user["id"], include_dismissed=False)
            
    return {"insights": existing}

@router.post("/{insight_id}/dismiss")
def dismiss(insight_id: int, user: dict = Depends(get_current_user)):
    success = dismiss_insight(insight_id, user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Insight not found")
    return {"message": "Insight dismissed"}
