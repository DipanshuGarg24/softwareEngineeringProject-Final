"""
Anonymous Chat Routes — Random matching, live polling chat
"""
import random
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from database import (chat_waiting_queue, chat_sessions, user_to_session,
                      sessions, users, new_id, now_iso)

router = APIRouter()

ALIASES = [
    "Mysterious Owl", "Cosmic Panda", "Silent Tiger", "Neon Fox",
    "Pixel Parrot", "Thunder Cat", "Shadow Wolf", "Crystal Bear",
    "Velvet Raven", "Quantum Duck", "Sapphire Lynx", "Blazing Koala",
    "Crimson Hawk", "Ember Phoenix", "Jade Dolphin", "Moonlit Gecko",
    "Arctic Falcon", "Golden Mantis", "Nebula Penguin", "Sonic Turtle",
]


def _get_uid(auth: str) -> str:
    token = auth.replace("Bearer ", "").strip()
    uid = sessions.get(token)
    if not uid: raise HTTPException(401, "Not authenticated")
    return uid


@router.get("/online")
def online_count():
    active = sum(1 for s in chat_sessions.values() if s["active"])
    waiting = len(chat_waiting_queue)
    # base = 15 + active * 2 + waiting + random.randint(0, 8)
    base = waiting + active
    return {"online_users": base, "waiting": waiting, "active_chats": active}


@router.post("/start")
def start_chat(authorization: str = Header(default="")):
    uid = _get_uid(authorization)

    # If user already in active session, return it
    if uid in user_to_session:
        sid = user_to_session[uid]
        s = chat_sessions.get(sid)
        if s and s["active"]:
            my_alias = s["aliases"].get(uid, "Anonymous")
            partner_uid = s["user1"] if s["user2"] == uid else s["user2"]
            partner_alias = s["aliases"].get(partner_uid, "Anonymous")
            return {"status": "matched", "session_id": sid,
                    "your_alias": my_alias, "partner_alias": partner_alias}

    # Remove from queue if already waiting
    chat_waiting_queue[:] = [w for w in chat_waiting_queue if w["user_id"] != uid]

    my_alias = random.choice(ALIASES)

    # Try to match with someone waiting
    for i, waiter in enumerate(chat_waiting_queue):
        if waiter["user_id"] != uid:
            # Match found!
            partner = chat_waiting_queue.pop(i)
            sid = new_id()
            chat_sessions[sid] = {
                "id": sid,
                "user1": partner["user_id"],
                "user2": uid,
                "aliases": {partner["user_id"]: partner["alias"], uid: my_alias},
                "messages": [{
                    "sender": "system", "alias": "system",
                    "text": f"🎉 You've been matched! This chat is anonymous. Say hi!",
                    "time": now_iso(),
                }],
                "active": True,
                "created_at": now_iso(),
            }
            user_to_session[uid] = sid
            user_to_session[partner["user_id"]] = sid
            return {
                "status": "matched", "session_id": sid,
                "your_alias": my_alias, "partner_alias": partner["alias"],
            }

    # No match — join queue
    chat_waiting_queue.append({"user_id": uid, "alias": my_alias})
    return {"status": "waiting", "your_alias": my_alias,
            "message": "Looking for a random IIT Bombian..."}


@router.get("/poll")
def poll_status(authorization: str = Header(default="")):
    """Waiting users poll this to check if matched."""
    uid = _get_uid(authorization)

    # Check if matched into a session
    if uid in user_to_session:
        sid = user_to_session[uid]
        s = chat_sessions.get(sid)
        if s and s["active"]:
            partner_uid = s["user1"] if s["user2"] == uid else s["user2"]
            return {
                "status": "matched", "session_id": sid,
                "your_alias": s["aliases"].get(uid, ""),
                "partner_alias": s["aliases"].get(partner_uid, ""),
            }

    # Still waiting
    in_queue = any(w["user_id"] == uid for w in chat_waiting_queue)
    return {"status": "waiting" if in_queue else "idle"}


class SendMsg(BaseModel):
    session_id: str
    text: str


@router.post("/send")
def send_message(msg: SendMsg, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    s = chat_sessions.get(msg.session_id)
    if not s: raise HTTPException(404, "Session not found")
    if not s["active"]: raise HTTPException(400, "Chat ended")
    if uid not in (s["user1"], s["user2"]):
        raise HTTPException(403, "Not in this chat")

    alias = s["aliases"].get(uid, "Anonymous")
    s["messages"].append({
        "sender": uid, "alias": alias,
        "text": msg.text, "time": now_iso(),
    })
    return {"message": "Sent", "total": len(s["messages"])}


@router.get("/messages/{session_id}")
def get_messages(session_id: str, after: int = 0, authorization: str = Header(default="")):
    """Get messages. Use after=N to get only new messages (long-polling style)."""
    uid = _get_uid(authorization)
    s = chat_sessions.get(session_id)
    if not s: raise HTTPException(404, "Session not found")
    if uid not in (s["user1"], s["user2"]):
        raise HTTPException(403, "Not in this chat")

    msgs = s["messages"][after:]
    # Replace sender uid with "me" or "partner" for the client
    client_msgs = []
    for m in msgs:
        if m["sender"] == "system":
            client_msgs.append({"type": "system", "text": m["text"], "time": m["time"]})
        elif m["sender"] == uid:
            client_msgs.append({"type": "mine", "alias": m["alias"], "text": m["text"], "time": m["time"]})
        else:
            client_msgs.append({"type": "theirs", "alias": m["alias"], "text": m["text"], "time": m["time"]})

    return {
        "session_id": session_id, "active": s["active"],
        "messages": client_msgs, "total": len(s["messages"]),
    }


@router.post("/end/{session_id}")
def end_chat(session_id: str, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    s = chat_sessions.get(session_id)
    if not s: raise HTTPException(404, "Not found")
    if uid not in (s["user1"], s["user2"]):
        raise HTTPException(403, "Not in this chat")

    s["active"] = False
    s["messages"].append({
        "sender": "system", "alias": "system",
        "text": "Chat ended. Start a new chat to meet another IIT Bombian!",
        "time": now_iso(),
    })

    # Cleanup session mapping
    for u in (s["user1"], s["user2"]):
        if user_to_session.get(u) == session_id:
            del user_to_session[u]

    return {"message": "Chat ended"}


@router.post("/leave-queue")
def leave_queue(authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    chat_waiting_queue[:] = [w for w in chat_waiting_queue if w["user_id"] != uid]
    return {"message": "Left queue"}
