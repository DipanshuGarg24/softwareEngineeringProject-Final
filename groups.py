"""
Events Routes — Standalone event posts (no groups)
"""
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from database import events_data, users, sessions, new_id, now_iso, get_user_safe, add_feed, time_ago

router = APIRouter()


def _get_uid(auth: str) -> str:
    token = auth.replace("Bearer ", "").strip()
    uid = sessions.get(token)
    if not uid: raise HTTPException(401, "Not authenticated")
    return uid


class EventCreate(BaseModel):
    title: str
    description: str = ""
    date: str
    location: str = ""


def _enrich(e: dict) -> dict:
    creator = get_user_safe(e["created_by"])
    return {
        **e,
        "creator_name": creator.get("name", "Unknown"),
        "creator_avatar": creator.get("avatar", ""),
        "creator_hostel": creator.get("hostel", ""),
        "rsvp_count": len(e.get("rsvp", [])),
        "time_ago": time_ago(e.get("created_at", "")),
    }


@router.get("/")
def list_events():
    results = [_enrich(e) for e in events_data.values()]
    return {"events": sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)}


@router.get("/my")
def my_events(authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    results = [_enrich(e) for e in events_data.values() if e["created_by"] == uid]
    return {"events": sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)}


@router.post("/")
def create_event(event: EventCreate, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    eid = new_id()
    events_data[eid] = {
        "id": eid, "title": event.title,
        "description": event.description, "date": event.date,
        "location": event.location, "rsvp": [uid],
        "created_by": uid, "created_at": now_iso(),
    }
    name = users[uid]["name"]
    add_feed("fa-calendar", "#7c3aed", "#ede9fe",
             f"<b>{name}</b> posted event: <b>{event.title}</b>", "event")
    return {"message": "Created", "event": _enrich(events_data[eid])}


@router.put("/{eid}/rsvp")
def rsvp_event(eid: str, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    e = events_data.get(eid)
    if not e: raise HTTPException(404, "Event not found")
    if uid in e["rsvp"]:
        e["rsvp"].remove(uid)
        return {"message": "RSVP removed", "rsvp_count": len(e["rsvp"]), "is_going": False}
    e["rsvp"].append(uid)
    return {"message": "RSVP confirmed", "rsvp_count": len(e["rsvp"]), "is_going": True}


# @router.delete("/{eid}")
# def delete_event(eid: str, authorization: str = Header(default="")):
#     uid = _get_uid(authorization)
#     e = events_data.get(eid)
#     if not e: raise HTTPException(404, "Not found")
#     if e["created_by"] != uid: raise HTTPException(403, "Only creator can delete")
#     del events_data[eid]
#     return {"message": "Deleted"}