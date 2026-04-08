# CampusHub — The All-in-One Campus Platform

**Team Keyboard** | CS 682 – Software Engineering | IIT Bombay

---

## 📁 Project Structure

```
campushub/
│
├── README.md
│
├── frontend/
│   └── index.html                  ← Open in browser (after starting backend)
│
└── backend/
    ├── main.py                     ← FastAPI entry point
    ├── database.py                 ← In-memory data store (all seed data)
    ├── requirements.txt            ← Python dependencies
    ├── uploads/                    ← Product images stored here
    │
    └── routes/
        ├── __init__.py
        ├── auth.py                 ← Register / Login / Profile (token-based)
        ├── dashboard.py            ← Live feed, stats, leaderboard, today's mess
        ├── campus_runner.py        ← P2P requests: create/accept/complete/cancel
        ├── marketplace.py          ← Buy/Sell with image upload, WhatsApp contact
        ├── cab_sharing.py          ← Cab pools: create/join/leave/cancel
        ├── mess_menu.py            ← Hostel-wise, day-wise menus
        ├── anonymous_chat.py       ← Random matching, polling-based live chat
        └── groups.py               ← Groups, events, RSVP
```

---

## 🚀 How to Run

### Step 1: Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API docs: http://localhost:8000/docs

### Step 2: Open Frontend
Open `frontend/index.html` directly in your browser.
Or use VS Code Live Server, or any HTTP server.

The frontend connects to `http://localhost:8000/api`.

### Demo Login Credentials
| Email                   | Password     |
|-------------------------|--------------|
| dipanshu@iitb.ac.in     | password123  |
| rahul@iitb.ac.in        | password123  |
| sneha@iitb.ac.in        | password123  |
| amit@iitb.ac.in         | password123  |
| priya@iitb.ac.in        | password123  |

---

## ✅ All Features — Fully Live via Backend API

### 1. Authentication (Token-Based)
- Login / Register with @iitb.ac.in email validation
- Bearer token stored in localStorage
- Auto-login on page reload
- All API calls authenticated

### 2. Dashboard
- Live campus feed (updates when actions happen)
- Stats cards (active requests, pools, listings)
- Karma leaderboard (sorted from backend)
- Today's mess menu

### 3. Campus Runner (P2P Help)
- Post requests with reward, category, locations, urgency
- Accept tasks from other users
- **My Requests** → Posted tab (mark complete/cancel) + Accepted tab
- Karma awarded on completion (backend updates user karma)
- Feed updates on every action

### 4. Marketplace (Buy & Sell)
- **Sell**: List items with title, price, category, condition, **product image upload**
- **My Listings**: View all your items, mark as sold, relist, or delete
- **Buy**: Browse with category filter, click item for full detail modal
- **WhatsApp Contact**: "Contact Seller on WhatsApp" deep link with pre-filled message
- Images saved to `backend/uploads/` and served via `/uploads/` route

### 5. Cab Sharing
- Create pools with destination, departure time, seat count
- Join / leave pools (with member avatars)
- Creator can cancel
- Auto-marks as "full" when seats fill up

### 6. Mess Menu
- 3 hostels (H12, H13, H3) × 7 days
- Toggle hostel and day tabs
- Shows breakfast, lunch, dinner

### 7. Anonymous Chat (Live Polling)
- Shows live online user count
- Click "Start Random Chat" → enters matching queue
- **If someone else is waiting** → instantly matched
- **If no one waiting** → polls every 2s until matched
- Both users get anonymous aliases (e.g., "Cosmic Panda")
- Messages poll every 1.5s from backend → truly live chat
- "End Chat" notifies both users
- Works across browser tabs / different users

### 8. Groups & Events
- Create public/private groups
- Join groups
- Create events within groups
- RSVP toggle (going / not going)
- Event count and attendee tracking

---

## 🏗 Architecture

```
┌──────────────────┐         ┌──────────────────┐
│   Frontend       │  HTTP   │   FastAPI Backend │
│   (index.html)   │◄───────►│   (main.py)      │
│   Vanilla JS     │  JSON   │                  │
│   Tailwind CSS   │         │   routes/         │
│                  │         │   ├── auth.py     │
│                  │         │   ├── runner.py   │
│  localStorage    │         │   ├── market.py   │
│  (auth token)    │         │   ├── cab.py      │
│                  │         │   ├── chat.py     │
│                  │         │   └── ...         │
│                  │         │                  │
│                  │         │   database.py     │
│                  │         │   (in-memory)     │
│                  │         │                  │
│                  │         │   uploads/        │
│                  │         │   (product images)│
└──────────────────┘         └──────────────────┘
```

### Why In-Memory?
This is a prototype for CS 682 demo. For production:
- Replace `database.py` dicts with PostgreSQL + SQLAlchemy
- Replace polling chat with WebSockets
- Add proper JWT with expiry
- Deploy on Render/Railway

---

## 👥 Team Keyboard

| Member           | Role                          |
|------------------|-------------------------------|
| Dipanshu Garg    | Backend Development           |
| Garima Jain      | Frontend & UI/UX Design       |
| Abhinandan Kumar | Testing & Quality Assurance   |
| Pratik Man Shah  | Research & Competitive Analysis|
