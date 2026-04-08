"""
CampusHub — Main FastAPI Application
======================================
Run: uvicorn main:app --reload --host 0.0.0.0 --port 8000
Frontend: open frontend/index.html in browser (or serve via LiveServer)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routes import auth, dashboard, campus_runner, marketplace, cab_sharing, mess_menu, anonymous_chat, groups

app = FastAPI(
    title="CampusHub API",
    description="The All-in-One Campus Platform — Live Backend",
    version="1.0.0",
)

# CORS — allow frontend on any port/origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded images
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Register all route modules
app.include_router(auth.router,           prefix="/api/auth",        tags=["Authentication"])
app.include_router(dashboard.router,      prefix="/api/dashboard",   tags=["Dashboard"])
app.include_router(campus_runner.router,  prefix="/api/runner",      tags=["Campus Runner"])
app.include_router(marketplace.router,    prefix="/api/marketplace", tags=["Marketplace"])
app.include_router(cab_sharing.router,    prefix="/api/cab",         tags=["Cab Sharing"])
app.include_router(mess_menu.router,      prefix="/api/mess",        tags=["Mess Menu"])
app.include_router(anonymous_chat.router, prefix="/api/chat",        tags=["Anonymous Chat"])
app.include_router(groups.router,         prefix="/api/groups",      tags=["Groups & Events"])


@app.get("/", tags=["Root"])
def root():
    return {"message": "CampusHub API is running", "docs": "/docs"}