"""
Dashboard Routes — Feed, Stats, Leaderboard
"""
from fastapi import APIRouter, HTTPException, Header
from database import (feed_items, users, runner_requests, cab_pools,
                      marketplace_listings, get_leaderboard, time_ago, mess_menus,
                      karma_store, sessions)
from datetime import datetime

router = APIRouter()

DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


def _get_uid(auth: str) -> str:
    token = auth.replace("Bearer ", "").strip()
    uid = sessions.get(token)
    if not uid: raise HTTPException(401, "Not authenticated")
    return uid


@router.get("/feed")
def get_feed():
    items = []
    for f in feed_items[:20]:
        items.append({**f, "time_ago": time_ago(f["time"])})
    return {"feed": items}


@router.get("/stats")
def get_stats():
    return {
        "active_requests": sum(1 for r in runner_requests.values() if r["status"] == "open"),
        "cab_pools": sum(1 for c in cab_pools.values() if c["status"] == "open"),
        "market_listings": sum(1 for m in marketplace_listings.values() if m["status"] == "available"),
        "total_users": len(users),
    }


@router.get("/leaderboard")
def leaderboard():
    return {"leaderboard": get_leaderboard()}


@router.get("/today-mess")
def today_mess(hostel: str = "H12"):
    day = DAYS[datetime.utcnow().weekday()]
    menu = mess_menus.get(hostel, {}).get(day, mess_menus.get(hostel, {}).get("Wednesday", {}))
    return {"hostel": hostel, "day": day, "menu": menu}


@router.get("/karma-store")
def get_karma_store():
    return {"items": karma_store}


@router.post("/karma-store/redeem/{item_id}")
def redeem_item(item_id: str, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    user = users.get(uid)
    if not user: raise HTTPException(404, "User not found")
    item = next((i for i in karma_store if i["id"] == item_id), None)
    if not item: raise HTTPException(404, "Item not found")
    if user["karma"] < item["cost"]:
        raise HTTPException(400, f"Not enough karma. Need {item['cost']}, have {user['karma']}.")
    user["karma"] -= item["cost"]
    return {"message": f"Redeemed {item['name']}! Remaining karma: {user['karma']}", "remaining_karma": user["karma"]}