from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.routers.auth import get_current_user
from tools.workflow_db import get_workflows, add_workflow, update_workflow_status, delete_workflow
from agents.orchestrator_agent import run_assistant
from tools.llm_client import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
import json

router = APIRouter()

class WorkflowRequest(BaseModel):
    nl_description: str

class WorkflowStatusRequest(BaseModel):
    enabled: bool

@router.get("")
def list_workflows(user: dict = Depends(get_current_user)):
    return {"workflows": get_workflows(user["id"])}

@router.post("")
def create_workflow(req: WorkflowRequest, user: dict = Depends(get_current_user)):
    # Parse NL to structured workflow
    llm = get_llm()
    prompt = f"""
    Convert the following natural language workflow description into JSON.
    Fields needed:
    - title (short name)
    - trigger_type (time_based or condition_based)
    - schedule (e.g., 'Every Monday at 9AM', or null)
    - condition (e.g., 'If it rains', or null)
    - action (What to do, e.g., 'send AI news summary')
    
    User: {req.nl_description}
    Respond ONLY in valid JSON.
    """
    try:
        res = llm.invoke([SystemMessage(content="You are a workflow parser."), HumanMessage(content=prompt)])
        content = res.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        
        wf_id = add_workflow(
            user_id=user["id"],
            title=data.get("title", "Untitled Workflow"),
            trigger_type=data.get("trigger_type", "condition_based"),
            schedule=data.get("schedule") or "",
            condition=data.get("condition") or "",
            action=data.get("action", "")
        )
        return {"message": "Workflow created", "id": wf_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse workflow: {str(e)}")

@router.put("/{workflow_id}")
def update_status(workflow_id: int, req: WorkflowStatusRequest, user: dict = Depends(get_current_user)):
    success = update_workflow_status(workflow_id, user["id"], req.enabled)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow updated"}

@router.delete("/{workflow_id}")
def delete_wf(workflow_id: int, user: dict = Depends(get_current_user)):
    success = delete_workflow(workflow_id, user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted"}

@router.post("/{workflow_id}/run")
def run_workflow(workflow_id: int, user: dict = Depends(get_current_user)):
    # Find workflow
    wfs = get_workflows(user["id"])
    wf = next((w for w in wfs if w["id"] == workflow_id), None)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Run the action through KAVI orchestrator
    response, intent, confidence, agent_runs = run_assistant(wf["action"], user_id=user["id"])
    
    return {
        "message": "Workflow executed manually.",
        "result": {
            "response": response,
            "agent_runs": agent_runs
        }
    }
