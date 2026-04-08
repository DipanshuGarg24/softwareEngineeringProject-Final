"""
Marketplace Routes — Buy/Sell with Image Upload
"""
import os
import shutil
from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from database import marketplace_listings, users, sessions, new_id, now_iso, time_ago, add_feed, get_user_safe

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

CATEGORY_ICONS = {
    "books": "fa-book", "electronics": "fa-laptop", "cycles": "fa-bicycle",
    "mattresses": "fa-bed", "clothing": "fa-shirt", "sports": "fa-football",
    "other": "fa-box",
}


def _get_uid(authorization: str) -> str:
    token = authorization.replace("Bearer ", "").strip()
    uid = sessions.get(token)
    if not uid: raise HTTPException(401, "Not authenticated")
    return uid


def _enrich(m: dict) -> dict:
    seller = get_user_safe(m["seller_id"])
    return {
        **m, "time_ago": time_ago(m["created_at"]),
        "seller_name": seller.get("name", "Unknown"),
        "seller_hostel": seller.get("hostel", ""),
        "seller_avatar": seller.get("avatar", ""),
        "seller_phone": seller.get("phone", ""),
        "icon": CATEGORY_ICONS.get(m.get("category", ""), "fa-box"),
    }


@router.get("/")
def list_all(category: str = "all", status: str = "available"):
    results = []
    for m in marketplace_listings.values():
        if m["status"] != status: continue
        if category != "all" and m.get("category") != category: continue
        results.append(_enrich(m))
    return {"listings": sorted(results, key=lambda x: x["created_at"], reverse=True)}


@router.post("/")
async def create_listing(
    title: str = Form(...),
    description: str = Form(""),
    price: int = Form(0),
    category: str = Form("other"),
    condition: str = Form("used"),
    image: Optional[UploadFile] = File(None),
    authorization: str = Header(default=""),
):
    uid = _get_uid(authorization)
    mid = new_id()
    image_path = None

    if image and image.filename:
        ext = image.filename.split(".")[-1] if "." in image.filename else "jpg"
        fname = f"{mid}.{ext}"
        fpath = os.path.join(UPLOAD_DIR, fname)
        with open(fpath, "wb") as f:
            content = await image.read()
            f.write(content)
        image_path = f"/uploads/{fname}"

    seller = users.get(uid, {})
    marketplace_listings[mid] = {
        "id": mid, "seller_id": uid, "title": title,
        "description": description, "price": price,
        "category": category, "condition": condition,
        "hostel": seller.get("hostel", ""), "image": image_path,
        "status": "available", "created_at": now_iso(),
    }
    add_feed("fa-tag", "#16a34a", "#dcfce7",
             f"<b>{seller.get('name','Someone')}</b> listed <b>{title}</b> for ₹{price}.", "market")
    return {"message": "Listed", "listing": _enrich(marketplace_listings[mid])}


@router.get("/my")
def my_listings(authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    results = [_enrich(m) for m in marketplace_listings.values() if m["seller_id"] == uid]
    return {"listings": sorted(results, key=lambda x: x["created_at"], reverse=True)}


@router.get("/contact/{listing_id}")
def get_contact(listing_id: str):
    m = marketplace_listings.get(listing_id)
    if not m: raise HTTPException(404, "Not found")
    seller = users.get(m["seller_id"], {})
    phone = seller.get("phone", "")
    msg = f"Hi! I'm interested in your CampusHub listing: {m['title']} (₹{m['price']})"
    return {
        "seller_name": seller.get("name"),
        "phone": phone,
        "whatsapp_url": f"https://wa.me/91{phone}?text={msg}",
    }


@router.get("/{listing_id}")
def get_listing(listing_id: str):
    m = marketplace_listings.get(listing_id)
    if not m: raise HTTPException(404, "Not found")
    return _enrich(m)


@router.put("/{listing_id}/sold")
def mark_sold(listing_id: str, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    m = marketplace_listings.get(listing_id)
    if not m: raise HTTPException(404, "Not found")
    if m["seller_id"] != uid: raise HTTPException(403, "Only seller can mark sold")
    m["status"] = "sold"
    return {"message": "Marked sold", "listing": _enrich(m)}


@router.put("/{listing_id}/relist")
def relist(listing_id: str, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    m = marketplace_listings.get(listing_id)
    if not m: raise HTTPException(404, "Not found")
    if m["seller_id"] != uid: raise HTTPException(403, "Only seller")
    m["status"] = "available"
    return {"message": "Relisted", "listing": _enrich(m)}


@router.delete("/{listing_id}")
def delete_listing(listing_id: str, authorization: str = Header(default="")):
    uid = _get_uid(authorization)
    m = marketplace_listings.get(listing_id)
    if not m: raise HTTPException(404, "Not found")
    if m["seller_id"] != uid: raise HTTPException(403, "Only seller")
    # Delete image file if exists
    if m.get("image"):
        img_path = os.path.join(UPLOAD_DIR, os.path.basename(m["image"]))
        if os.path.exists(img_path):
            os.remove(img_path)
    del marketplace_listings[listing_id]
    return {"message": "Deleted"}