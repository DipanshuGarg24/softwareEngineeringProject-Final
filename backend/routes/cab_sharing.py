"""
Cab Sharing Routes — Create / Join / Leave / My Rides
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from database import cab_pools, users, sessions, new_id, now_iso, add_feed, get_user_safe

router = APIRouter()

CANCEL_PENALTY = 50  # karma deducted when a joiner leaves


def _get_uid(auth: str) -> str:
    token = auth.replace("Bearer ", "").strip()
    uid = sessions.get(token)
    if not uid: raise HTTPException(401, "Not authenticated")
    return uid


class CabCreate(BaseModel):
    destination: str
    destination_icon: str = "fa-location-dot"
    departure_time: str
    total_seats: int = 4


def _enrich(c: dict) -> dict:
    creator = get_user_safe(c["creator_id"])
    member_details = []
    for uid in c["members"]:
        u = get_user_safe(uid)
        member_details.append({
            "id": uid, "name": u.get("name", ""), "avatar": u.get("avatar", ""),
            "phone": u.get("phone", ""), "hostel": u.get("hostel", ""),
            "email": u.get("email", ""),
        })
    return {
        **c,
        "creator_name": creator.get("name", "Unknown"),
        "creator_phone": creator.get("phone", ""),
        "creator_hostel": creator.get("hostel", ""),
        "seats_left": c["total_seats"] - len(c["members"]),
        "member_details": member_details,
    }


@router.get("/")
def list_pools():
    results = [_enrich(c) for c in cab_pools.values() if c["status"] in ("open", "full")]
    return {"pools": sorted(results, key=lambda x: x["created_at"], reverse=True)}


@router.get("/my")
def my_rides(authorization: str = Header(default="")):
    """All rides where I'm a member or creator, any status."""
    uid = _get_uid(authorization)
    results = [_enrich(c) for c in cab_pools.values() if uid in c["members"] or c["creator_id"] == uid]
    return {"pools": sorted(results, key=lambda x: x["created_at"], reverse=True)}


@router.post("/")
def create_pool(pool: CabCreate, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    cid = new_id()
    cab_pools[cid] = {
        "id": cid, "creator_id": uid, "destination": pool.destination,
        "destination_icon": pool.destination_icon, "departure_time": pool.departure_time,
        "total_seats": pool.total_seats, "members": [uid],
        "status": "open", "created_at": now_iso(),
    }
    name = users[uid]["name"]
    add_feed("fa-taxi", "#d97706", "#fef3c7",
             f"<b>{name}</b> created cab pool to <b>{pool.destination}</b>.", "cab")
    return {"message": "Created", "pool": _enrich(cab_pools[cid])}


@router.put("/{cid}/join")
def join_pool(cid: str, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    c = cab_pools.get(cid)
    if not c: raise HTTPException(404, "Not found")
    if c["status"] not in ("open",): raise HTTPException(400, "Not open")
    if uid in c["members"]: raise HTTPException(400, "Already joined")
    if len(c["members"]) >= c["total_seats"]: raise HTTPException(400, "Full")
    c["members"].append(uid)
    if len(c["members"]) >= c["total_seats"]:
        c["status"] = "full"
    return {"message": "Joined", "pool": _enrich(c)}


@router.put("/{cid}/leave")
def leave_pool(cid: str, authorization: str = Header(default="")):
    """Non-creator leaves. Deducts karma as penalty."""
    uid = _get_uid(authorization)
    c = cab_pools.get(cid)
    if not c: raise HTTPException(404, "Not found")
    if uid not in c["members"]: raise HTTPException(400, "Not a member")
    if uid == c["creator_id"]: raise HTTPException(400, "Creator can't leave; cancel the pool instead")
    c["members"].remove(uid)
    if c["status"] == "full":
        c["status"] = "open"
    # Deduct karma penalty
    if uid in users:
        users[uid]["karma"] = max(0, users[uid]["karma"] - CANCEL_PENALTY)
    return {
        "message": f"Left pool. {CANCEL_PENALTY} karma deducted.",
        "pool": _enrich(c),
        "karma_deducted": CANCEL_PENALTY,
    }


@router.put("/{cid}/cancel")
def cancel_pool(cid: str, authorization: str = Header(default="")):
    """Creator cancels entire pool."""
    uid = _get_uid(authorization)
    c = cab_pools.get(cid)
    if not c: raise HTTPException(404, "Not found")
    if c["creator_id"] != uid: raise HTTPException(403, "Only creator can cancel")
    c["status"] = "cancelled"
    return {"message": "Pool cancelled"}