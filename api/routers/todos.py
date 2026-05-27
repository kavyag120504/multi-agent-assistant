from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.routers.auth import get_current_user
from tools.todo_db import get_tasks, add_task, complete_task, delete_task

router = APIRouter()

class TodoRequest(BaseModel):
    task: str
    due_date: Optional[str] = None
    priority: str = "normal"

@router.get("")
def list_todos(filter: str = "pending", user: dict = Depends(get_current_user)):
    tasks = get_tasks(filter=filter, user_id=user["id"])
    return {"tasks": tasks}

@router.post("")
def create_todo(req: TodoRequest, user: dict = Depends(get_current_user)):
    task_id = add_task(
        task=req.task,
        user_id=user["id"],
        due_date=req.due_date,
        priority=req.priority
    )
    return {"message": "Task created", "id": task_id}

@router.put("/{task_id}/complete")
def complete_todo(task_id: int, user: dict = Depends(get_current_user)):
    success = complete_task(task_id, user_id=user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or already completed")
    return {"message": "Task completed"}

@router.delete("/{task_id}")
def delete_todo(task_id: int, user: dict = Depends(get_current_user)):
    success = delete_task(task_id, user_id=user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}
