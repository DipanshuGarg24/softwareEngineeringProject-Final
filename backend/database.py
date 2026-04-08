"""
CampusHub — In-Memory Data Store
==================================
All data lives in Python dicts. Resets on server restart.
For production, replace with PostgreSQL + SQLAlchemy.
"""

import uuid
from datetime import datetime

def new_id() -> str:
    return uuid.uuid4().hex[:8]

def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

def time_ago(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", ""))
        diff = datetime.utcnow() - dt
        secs = int(diff.total_seconds())
        if secs < 60: return "Just now"
        if secs < 3600: return f"{secs // 60} mins ago"
        if secs < 86400: return f"{secs // 3600} hours ago"
        return f"{secs // 86400} days ago"
    except:
        return "Recently"

# ─── USERS ─────────────────────────────────────────────────────
users: dict[str, dict] = {
    "u001": {
        "id": "u001", "name": "Dipanshu Garg", "email": "dipanshu@iitb.ac.in",
        "password": "password123", "hostel": "H12", "department": "CSE",
        "year": "M.Tech", "karma": 1240, "phone": "9876543210",
        "avatar": "https://ui-avatars.com/api/?name=Dipanshu+G&background=0D8ABC&color=fff",
    },
    "u002": {
        "id": "u002", "name": "Rahul Gupta", "email": "rahul@iitb.ac.in",
        "password": "password123", "hostel": "H3", "department": "EE",
        "year": "B.Tech 3rd", "karma": 890, "phone": "9876543211",
        "avatar": "https://ui-avatars.com/api/?name=Rahul+G&background=E91E63&color=fff",
    },
    "u003": {
        "id": "u003", "name": "Sneha Patil", "email": "sneha@iitb.ac.in",
        "password": "password123", "hostel": "H10", "department": "ME",
        "year": "B.Tech 4th", "karma": 1560, "phone": "9876543212",
        "avatar": "https://ui-avatars.com/api/?name=Sneha+P&background=4CAF50&color=fff",
    },
    "u004": {
        "id": "u004", "name": "Amit Kumar", "email": "amit@iitb.ac.in",
        "password": "password123", "hostel": "H5", "department": "CSE",
        "year": "PhD", "karma": 2100, "phone": "9876543213",
        "avatar": "https://ui-avatars.com/api/?name=Amit+K&background=FF9800&color=fff",
    },
    "u005": {
        "id": "u005", "name": "Priya Sharma", "email": "priya@iitb.ac.in",
        "password": "password123", "hostel": "H13", "department": "CH",
        "year": "M.Tech", "karma": 670, "phone": "9876543214",
        "avatar": "https://ui-avatars.com/api/?name=Priya+S&background=9C27B0&color=fff",
    },
}

# Active login sessions: token -> user_id
sessions: dict[str, str] = {}

# ─── CAMPUS RUNNER ─────────────────────────────────────────────
runner_requests: dict[str, dict] = {
    "r001": {
        "id": "r001", "poster_id": "u002", "title": "Need 2 Samosas & Tea",
        "description": "Studying for finals. Can someone bring snacks from H12 canteen to H3?",
        "reward": 30, "category": "food", "from_location": "H12 Canteen",
        "to_location": "H3 Room 214", "status": "open", "accepted_by": None,
        "is_urgent": True, "created_at": now_iso(),
    },
    "r002": {
        "id": "r002", "poster_id": "u003", "title": "Printout Delivery",
        "description": "Need printouts from CSE department office brought to H10 gate.",
        "reward": 20, "category": "delivery", "from_location": "CSE Dept Office",
        "to_location": "H10 Gate", "status": "open", "accepted_by": None,
        "is_urgent": False, "created_at": now_iso(),
    },
    "r003": {
        "id": "r003", "poster_id": "u004", "title": "Parcel from Main Gate",
        "description": "Amazon parcel at main gate security. Will share OTP.",
        "reward": 40, "category": "delivery", "from_location": "Main Gate Security",
        "to_location": "H5 Room 310", "status": "open", "accepted_by": None,
        "is_urgent": True, "created_at": now_iso(),
    },
    "r004": {
        "id": "r004", "poster_id": "u005", "title": "Coffee from Cafe 92",
        "description": "Need a large cappuccino. I'm in H13 library, 2nd floor.",
        "reward": 15, "category": "food", "from_location": "Cafe 92",
        "to_location": "H13 Library", "status": "open", "accepted_by": None,
        "is_urgent": False, "created_at": now_iso(),
    },
}

# ─── MARKETPLACE ───────────────────────────────────────────────
marketplace_listings: dict[str, dict] = {
    "m001": {
        "id": "m001", "seller_id": "u001", "title": "Hercules Cycle",
        "description": "Good condition, new tyres. Selling because graduating.",
        "price": 2500, "category": "cycles", "condition": "used",
        "hostel": "H12", "image": None, "status": "available", "created_at": now_iso(),
    },
    "m002": {
        "id": "m002", "seller_id": "u003", "title": "GATE CSE Notes",
        "description": "Complete Made Easy handwritten notes for CSE.",
        "price": 500, "category": "books", "condition": "new",
        "hostel": "H10", "image": None, "status": "available", "created_at": now_iso(),
    },
    "m003": {
        "id": "m003", "seller_id": "u004", "title": "JBL Bluetooth Speaker",
        "description": "JBL Flip 5, barely used. Original box and charger included.",
        "price": 3200, "category": "electronics", "condition": "like_new",
        "hostel": "H5", "image": None, "status": "available", "created_at": now_iso(),
    },
    "m004": {
        "id": "m004", "seller_id": "u002", "title": "Mattress (Single)",
        "description": "Sleepwell mattress, 6x3 ft, used for 1 year only.",
        "price": 1800, "category": "mattresses", "condition": "used",
        "hostel": "H3", "image": None, "status": "available", "created_at": now_iso(),
    },
    "m005": {
        "id": "m005", "seller_id": "u005", "title": "Scientific Calculator",
        "description": "Casio FX-991EX, perfect for exams. All functions working.",
        "price": 800, "category": "electronics", "condition": "used",
        "hostel": "H13", "image": None, "status": "available", "created_at": now_iso(),
    },
    "m006": {
        "id": "m006", "seller_id": "u004", "title": "Cricket Kit (Full)",
        "description": "SG bat, pads, gloves, helmet. Good condition.",
        "price": 4500, "category": "sports", "condition": "used",
        "hostel": "H5", "image": None, "status": "available", "created_at": now_iso(),
    },
}

# ─── CAB POOLS ─────────────────────────────────────────────────
cab_pools: dict[str, dict] = {
    "c001": {
        "id": "c001", "creator_id": "u004", "destination": "Mumbai Airport (T2)",
        "destination_icon": "fa-plane-departure", "departure_time": "Today, 5:00 PM",
        "total_seats": 4, "members": ["u004", "u002"], "status": "open", "created_at": now_iso(),
    },
    "c002": {
        "id": "c002", "creator_id": "u005", "destination": "Dadar Station",
        "destination_icon": "fa-train", "departure_time": "Tomorrow, 9:00 AM",
        "total_seats": 4, "members": ["u005", "u002", "u003"], "status": "open", "created_at": now_iso(),
    },
    "c003": {
        "id": "c003", "creator_id": "u001", "destination": "Pune (Shivajinagar)",
        "destination_icon": "fa-bus", "departure_time": "Mar 21, 6:00 AM",
        "total_seats": 3, "members": ["u001"], "status": "open", "created_at": now_iso(),
    },
}

# ─── MESS MENUS ────────────────────────────────────────────────
# H3, H12, H13 have manually curated menus; rest are generated
_base_menus = {
    "Monday":    {"breakfast": "Poha, Jalebi, Tea/Coffee/Milk", "lunch": "Dal Fry, Aloo Matar, Rice, Chapati, Salad", "dinner": "Chicken Curry / Paneer Tikka, Roti, Rice, Ice Cream"},
    "Tuesday":   {"breakfast": "Idli Sambar, Chutney, Tea/Coffee/Milk", "lunch": "Chole, Jeera Rice, Chapati, Raita", "dinner": "Fish Curry / Dal Makhani, Roti, Pulao, Kheer"},
    "Wednesday": {"breakfast": "Aloo Paratha, Curd, Pickle, Tea/Coffee/Milk", "lunch": "Rajma Masala, Aloo Gobhi, Rice, Chapati, Buttermilk", "dinner": "Paneer Butter Masala / Egg Curry, Fried Rice, Gulab Jamun"},
    "Thursday":  {"breakfast": "Upma, Vada, Chutney, Tea/Coffee/Milk", "lunch": "Sambar, Beans Poriyal, Rice, Chapati, Papad", "dinner": "Mutton Curry / Soya Chunks, Roti, Rice, Fruit Custard"},
    "Friday":    {"breakfast": "Bread Pakora, Sauce, Tea/Coffee/Milk", "lunch": "Kadhi Pakora, Aloo Gobi, Rice, Chapati", "dinner": "Biryani (Veg/Non-Veg), Raita, Salad"},
    "Saturday":  {"breakfast": "Chole Bhature, Lassi", "lunch": "Mix Veg, Dal Tadka, Rice, Chapati", "dinner": "Butter Chicken / Shahi Paneer, Naan, Pulao, Rasgulla"},
    "Sunday":    {"breakfast": "Dosa, Sambar, Chutney, Tea/Coffee/Milk", "lunch": "Pav Bhaji, Rice, Salad", "dinner": "Special Thali: Paneer/Chicken, 3 Rotis, Rice, Dal, Sweet"},
}
_h13_menu = {
    "Monday":    {"breakfast": "Upma, Banana, Tea/Coffee", "lunch": "Toor Dal, Bhindi Fry, Rice, Chapati", "dinner": "Egg Bhurji / Aloo Gobi, Roti, Rice"},
    "Tuesday":   {"breakfast": "Paratha, Curd, Tea/Coffee", "lunch": "Rajma, Cabbage Sabzi, Rice, Chapati", "dinner": "Chicken Curry / Palak Paneer, Roti, Rice, Halwa"},
    "Wednesday": {"breakfast": "Poha, Sprouts, Tea/Coffee", "lunch": "Chole, Baingan Bharta, Rice, Chapati", "dinner": "Fish Fry / Paneer Do Pyaza, Roti, Jeera Rice"},
    "Thursday":  {"breakfast": "Idli, Sambar, Tea/Coffee", "lunch": "Moong Dal, Mix Veg, Rice, Chapati", "dinner": "Keema / Mushroom Masala, Roti, Pulao, Gulab Jamun"},
    "Friday":    {"breakfast": "Sandwich, Juice, Tea/Coffee", "lunch": "Sambar, Potato Fry, Rice, Chapati", "dinner": "Veg/Non-Veg Biryani, Raita"},
    "Saturday":  {"breakfast": "Aloo Puri, Pickle, Tea/Coffee", "lunch": "Dal Fry, Gobi Matar, Rice, Chapati", "dinner": "Butter Chicken / Malai Kofta, Naan, Rice, Ice Cream"},
    "Sunday":    {"breakfast": "Masala Dosa, Chutney, Tea/Coffee", "lunch": "Pav Bhaji, Lemon Rice", "dinner": "Special Non-Veg / Paneer Thali, Sweet"},
}
_h3_menu = {
    "Monday":    {"breakfast": "Aloo Paratha, Curd, Tea/Coffee", "lunch": "Arhar Dal, Sev Tamatar, Rice, Chapati", "dinner": "Egg Curry / Matar Paneer, Roti, Rice"},
    "Tuesday":   {"breakfast": "Poha, Sev, Tea/Coffee", "lunch": "Chana Dal, Lauki Sabzi, Rice, Chapati", "dinner": "Chicken Curry / Kadai Paneer, Roti, Rice, Seviyan"},
    "Wednesday": {"breakfast": "Uttapam, Sambar, Tea/Coffee", "lunch": "Rajma, Aloo Fry, Rice, Chapati, Papad", "dinner": "Fish Curry / Paneer Bhurji, Roti, Veg Pulao"},
    "Thursday":  {"breakfast": "Methi Paratha, Butter, Tea/Coffee", "lunch": "Dal Palak, Cabbage Peas, Rice, Chapati", "dinner": "Mutton / Soya Chaap, Roti, Rice, Kheer"},
    "Friday":    {"breakfast": "Medu Vada, Sambar, Tea/Coffee", "lunch": "Kadhi, Bhindi Masala, Rice, Chapati", "dinner": "Biryani (Chicken/Veg), Raita, Onion Salad"},
    "Saturday":  {"breakfast": "Chole Bhature, Lassi", "lunch": "Mix Veg, Moong Dal, Rice, Chapati", "dinner": "Butter Chicken / Paneer Lababdar, Naan, Pulao, Jalebi"},
    "Sunday":    {"breakfast": "Dosa, Coconut Chutney, Tea/Coffee", "lunch": "Aloo Baingan, Dal Tadka, Rice, Puri", "dinner": "Sunday Special Thali"},
}

mess_menus: dict[str, dict] = {}
for i in range(1, 23):
    key = f"H{i}"
    if i == 3: mess_menus[key] = _h3_menu
    elif i == 12: mess_menus[key] = _base_menus
    elif i == 13: mess_menus[key] = _h13_menu
    else: mess_menus[key] = _base_menus  # other hostels use base menu

# ─── ANONYMOUS CHAT ────────────────────────────────────────────
# waiting_queue: list of {user_id, alias, waiting_id}
chat_waiting_queue: list[dict] = []
# active sessions: session_id -> {user1, user2, aliases, messages, active}
chat_sessions: dict[str, dict] = {}
# track which session a user is currently in
user_to_session: dict[str, str] = {}

# ─── GROUPS & EVENTS ──────────────────────────────────────────
# Groups removed — events are standalone posts now
groups_data: dict[str, dict] = {}   # kept empty for import compatibility

events_data: dict[str, dict] = {
    "e001": {
        "id": "e001", "title": "Weekly Coding Contest #14",
        "description": "Codeforces Div 2 style, 5 problems, 2 hours. Open to all!",
        "date": "Mar 22, 6:00 PM", "location": "LC 101",
        "rsvp": ["u001", "u004", "u002"], "created_by": "u004", "created_at": now_iso(),
    },
    "e002": {
        "id": "e002", "title": "Inter-Hostel Cricket Finals",
        "description": "H12 vs H3 — Cricket ground behind SAC. Come cheer!",
        "date": "Mar 25, 4:00 PM", "location": "Cricket Ground",
        "rsvp": ["u002", "u001"], "created_by": "u002", "created_at": now_iso(),
    },
    "e003": {
        "id": "e003", "title": "AI/ML Workshop — Intro to Transformers",
        "description": "Hands-on workshop covering attention mechanisms, BERT, GPT. Bring your laptop.",
        "date": "Mar 28, 3:00 PM", "location": "SOM Seminar Hall",
        "rsvp": ["u001", "u003"], "created_by": "u001", "created_at": now_iso(),
    },
    "e004": {
        "id": "e004", "title": "H12 Movie Night — Interstellar",
        "description": "Projector screening at H12 common room. Popcorn provided!",
        "date": "Mar 23, 9:00 PM", "location": "H12 Common Room",
        "rsvp": ["u005", "u001", "u002", "u004"], "created_by": "u005", "created_at": now_iso(),
    },
}

# ─── KARMA STORE ──────────────────────────────────────────────
karma_store: list[dict] = [
    {"id": "ks01", "name": "Best Campus Runner T-Shirt", "description": "Exclusive CampusHub tee with your name", "cost": 2500, "icon": "fa-shirt", "color": "#2563eb"},
    {"id": "ks02", "name": "CampusHub Pen Set", "description": "Premium pen set with CampusHub branding", "cost": 500, "icon": "fa-pen", "color": "#16a34a"},
    {"id": "ks03", "name": "Coffee Voucher (Cafe 92)", "description": "Free coffee at campus cafe", "cost": 200, "icon": "fa-mug-hot", "color": "#d97706"},
    {"id": "ks04", "name": "Notebook + Stickers Pack", "description": "Ruled notebook with cool IIT stickers", "cost": 350, "icon": "fa-book", "color": "#7c3aed"},
    {"id": "ks05", "name": "Campus Runner Hoodie", "description": "Limited edition hoodie for top runners", "cost": 5000, "icon": "fa-vest-patches", "color": "#dc2626"},
    {"id": "ks06", "name": "Movie Night Pass (5 shows)", "description": "Free entry to 5 hostel movie screenings", "cost": 800, "icon": "fa-film", "color": "#0891b2"},
    {"id": "ks07", "name": "Canteen Meal Coupon (5)", "description": "5 free meals at any hostel canteen", "cost": 1500, "icon": "fa-utensils", "color": "#ea580c"},
    {"id": "ks08", "name": "CampusHub Cap", "description": "Snapback cap with CampusHub logo", "cost": 1000, "icon": "fa-hat-cowboy", "color": "#4f46e5"},
]

# ─── LIVE FEED ─────────────────────────────────────────────────
feed_items: list[dict] = [
    {"id": "f001", "type": "runner", "icon": "fa-utensils", "color": "#2563eb", "bg": "#dbeafe",
     "text": "<b>Rohan K.</b> accepted a delivery for <b>H3 Canteen</b>.", "time": now_iso()},
    {"id": "f002", "type": "cab", "icon": "fa-taxi", "color": "#d97706", "bg": "#fef3c7",
     "text": "<b>New Cab Pool</b> to Mumbai Airport (T2) tomorrow 6 AM.", "time": now_iso()},
    {"id": "f003", "type": "lost", "icon": "fa-exclamation", "color": "#dc2626", "bg": "#fee2e2",
     "text": "<b>Lost & Found:</b> Blue water bottle in Lecture Hall Complex.", "time": now_iso()},
    {"id": "f004", "type": "market", "icon": "fa-tag", "color": "#16a34a", "bg": "#dcfce7",
     "text": "<b>Sneha P.</b> listed <b>GATE CSE Notes</b> for ₹500.", "time": now_iso()},
    {"id": "f005", "type": "event", "icon": "fa-calendar", "color": "#7c3aed", "bg": "#ede9fe",
     "text": "<b>Coding Club:</b> Contest #14 Saturday 6 PM, LC 101.", "time": now_iso()},
]

# ─── HELPERS ───────────────────────────────────────────────────
def get_user_safe(uid: str) -> dict:
    """Return user without password."""
    u = users.get(uid)
    if not u: return {}
    return {k: v for k, v in u.items() if k != "password"}

def get_leaderboard() -> list[dict]:
    sorted_users = sorted(users.values(), key=lambda u: u["karma"], reverse=True)
    return [
        {"rank": i+1, "id": u["id"], "name": u["name"], "hostel": u["hostel"],
         "karma": u["karma"], "avatar": u["avatar"]}
        for i, u in enumerate(sorted_users)
    ]

def add_feed(icon, color, bg, text, feed_type="general"):
    feed_items.insert(0, {
        "id": new_id(), "type": feed_type, "icon": icon,
        "color": color, "bg": bg, "text": text, "time": now_iso(),
    })
    if len(feed_items) > 50:
        feed_items.pop()