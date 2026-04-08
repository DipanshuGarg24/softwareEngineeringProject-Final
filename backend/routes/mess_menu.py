"""
Mess Menu Routes
"""
from fastapi import APIRouter, HTTPException
from database import mess_menus
from datetime import datetime

router = APIRouter()
DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


@router.get("/hostels")
def list_hostels():
    return {"hostels": list(mess_menus.keys())}


@router.get("/")
def get_menu(hostel: str = "H12", day: str = ""):
    if hostel not in mess_menus:
        raise HTTPException(404, f"No menu for {hostel}")
    if not day:
        day = DAYS[datetime.utcnow().weekday()]
    menu = mess_menus[hostel].get(day)
    if not menu:
        raise HTTPException(404, f"No menu for {day}")
    return {"hostel": hostel, "day": day, "menu": menu}


@router.get("/week/{hostel}")
def get_week(hostel: str):
    if hostel not in mess_menus:
        raise HTTPException(404, f"No menu for {hostel}")
    return {"hostel": hostel, "week": mess_menus[hostel], "days": DAYS}
