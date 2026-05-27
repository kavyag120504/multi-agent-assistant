from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
import os
from tools.auth_db import register_user, login_user, get_user_by_id

# JWT settings
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    display_name: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

def create_jwt_token(user_id: int, username: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload.get("sub"))
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register")
def register(req: RegisterRequest):
    success, message = register_user(req.username, req.display_name, req.password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.post("/login")
def login(req: LoginRequest):
    success, message, user = login_user(req.username, req.password)
    if not success:
        raise HTTPException(status_code=401, detail=message)
    
    token = create_jwt_token(user["id"], user["username"])
    return {
        "message": message,
        "token": token,
        "user": user
    }

@router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    return user
