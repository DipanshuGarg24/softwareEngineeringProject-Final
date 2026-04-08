"""
Campus Runner Routes — P2P Help & Delivery
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from database import runner_requests, users, sessions, new_id, now_iso, time_ago, add_feed, get_user_safe

router = APIRouter()


def _get_uid(authorization: str) -> str:
    token = authorization.replace("Bearer ", "").strip()
    uid = sessions.get(token)
    if not uid: raise HTTPException(401, "Not authenticated")
    return uid


class RunnerCreate(BaseModel):
    title: str
    description: str
    reward: int = 20
    category: str = "general"
    from_location: str = ""
    to_location: str = ""
    is_urgent: bool = False


def _enrich(r: dict) -> dict:
    poster = get_user_safe(r["poster_id"])
    acceptor = get_user_safe(r.get("accepted_by") or "") if r.get("accepted_by") else {}
    return {
        **r, "time_ago": time_ago(r["created_at"]),
        "poster_name": poster.get("name", "Unknown"),
        "poster_hostel": poster.get("hostel", ""),
        "poster_avatar": poster.get("avatar", ""),
        "poster_phone": poster.get("phone", ""),
        "poster_email": poster.get("email", ""),
        "acceptor_name": acceptor.get("name", ""),
        "acceptor_avatar": acceptor.get("avatar", ""),
        "acceptor_phone": acceptor.get("phone", ""),
        "acceptor_hostel": acceptor.get("hostel", ""),
        "acceptor_email": acceptor.get("email", ""),
    }


@router.get("/")
def list_requests(status: str = "open"):
    results = [_enrich(r) for r in runner_requests.values() if r["status"] == status]
    return {"requests": sorted(results, key=lambda x: x["created_at"], reverse=True)}


@router.post("/")
def create_request(req: RunnerCreate, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    rid = new_id()
    runner_requests[rid] = {
        "id": rid, "poster_id": uid, "title": req.title,
        "description": req.description, "reward": req.reward,
        "category": req.category, "from_location": req.from_location,
        "to_location": req.to_location, "status": "open",
        "accepted_by": None, "is_urgent": req.is_urgent, "created_at": now_iso(),
    }
    name = users[uid]["name"]
    add_feed("fa-person-running", "#2563eb", "#dbeafe",
             f"<b>{name}</b> posted: <b>{req.title}</b>", "runner")
    return {"message": "Created", "request": _enrich(runner_requests[rid])}


@router.get("/my/posted")
def my_posted(authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    results = [_enrich(r) for r in runner_requests.values() if r["poster_id"] == uid]
    return {"requests": sorted(results, key=lambda x: x["created_at"], reverse=True)}


@router.get("/my/accepted")
def my_accepted(authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    results = [_enrich(r) for r in runner_requests.values() if r["accepted_by"] == uid]
    return {"requests": sorted(results, key=lambda x: x["created_at"], reverse=True)}


@router.put("/{rid}/accept")
def accept_request(rid: str, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    r = runner_requests.get(rid)
    if not r: raise HTTPException(404, "Not found")
    if r["status"] != "open": raise HTTPException(400, "Not open")
    if r["poster_id"] == uid: raise HTTPException(400, "Can't accept own request")
    r["status"] = "accepted"
    r["accepted_by"] = uid
    name = users[uid]["name"]
    add_feed("fa-check", "#16a34a", "#dcfce7",
             f"<b>{name}</b> accepted: <b>{r['title']}</b>", "runner")
    return {"message": "Accepted", "request": _enrich(r)}


@router.put("/{rid}/complete")
def complete_request(rid: str, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    r = runner_requests.get(rid)
    if not r: raise HTTPException(404, "Not found")
    if r["status"] != "accepted": raise HTTPException(400, "Must be accepted first")
    if r["poster_id"] != uid: raise HTTPException(403, "Only poster can mark complete")
    r["status"] = "completed"
    if r["accepted_by"] and r["accepted_by"] in users:
        users[r["accepted_by"]]["karma"] += r["reward"]
    return {"message": "Completed! Karma awarded.", "request": _enrich(r)}


@router.put("/{rid}/cancel")
def cancel_request(rid: str, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    r = runner_requests.get(rid)
    if not r: raise HTTPException(404, "Not found")
    if r["poster_id"] != uid: raise HTTPException(403, "Only poster can cancel")
    r["status"] = "cancelled"
    return {"message": "Cancelled", "request": _enrich(r)}