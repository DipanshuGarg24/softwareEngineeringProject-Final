"""
Auth Routes — Register / Login / Profile
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from database import users, sessions, new_id, now_iso, get_user_safe
from typing import Optional

router = APIRouter()


class RegisterReq(BaseModel):
    name: str
    email: str
    password: str
    hostel: str
    department: str
    year: str
    phone: str = ""


class LoginReq(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    hostel: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    phone: Optional[str] = None


def get_current_user(authorization: str = Header(default="")) -> dict:
    """Extract user from Bearer token."""
    token = authorization.replace("Bearer ", "").strip()
    uid = sessions.get(token)
    if not uid or uid not in users:
        raise HTTPException(401, "Not authenticated")
    return users[uid]


@router.post("/register")
def register(req: RegisterReq):
    if not req.email.endswith("@iitb.ac.in"):
        raise HTTPException(400, "Only @iitb.ac.in emails allowed")
    for u in users.values():
        if u["email"] == req.email:
            raise HTTPException(400, "Email already registered")
    uid = new_id()
    token = f"tok-{uid}-{new_id()}"
    users[uid] = {
        "id": uid, "name": req.name, "email": req.email,
        "password": req.password, "hostel": req.hostel,
        "department": req.department, "year": req.year,
        "karma": 0, "phone": req.phone,
        "avatar": f"https://ui-avatars.com/api/?name={req.name.replace(' ', '+')}&background=0D8ABC&color=fff",
    }
    sessions[token] = uid
    return {"token": token, "user": get_user_safe(uid)}


@router.post("/login")
def login(req: LoginReq):
    for u in users.values():
        if u["email"] == req.email and u["password"] == req.password:
            token = f"tok-{u['id']}-{new_id()}"
            sessions[token] = u["id"]
            return {"token": token, "user": get_user_safe(u["id"])}
    raise HTTPException(401, "Invalid email or password")


@router.get("/me")
def get_me(authorization: str = Header(default="")):
    user = get_current_user(authorization)
    return get_user_safe(user["id"])


@router.put("/me")
def update_me(update: ProfileUpdate, authorization: str = Header(default="")):
    user = get_current_user(authorization)
    for field, val in update.model_dump(exclude_none=True).items():
        user[field] = val
    return {"message": "Updated", "user": get_user_safe(user["id"])}