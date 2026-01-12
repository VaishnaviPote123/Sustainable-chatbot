# backend/app.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from rag import create_rag, rebuild_rag
import logging

# Load environment variables from .env (if present)
load_dotenv()

# basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from database import (
    init_db,
    get_user,
    create_user,
    get_leaderboard,
    log_carbon,
    set_challenge_of_day,
    get_challenge_of_day,
    add_reminder,
    get_user_reminders,
    toggle_reminder,
)

# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize DB, Groq client and RAG vectorstore on app startup."""
    try:
        logger.info("Initializing database...")
        init_db()

        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY not set in environment")

        logger.info("Initializing Groq client...")
        client = Groq(api_key=GROQ_API_KEY)
        app.state.client = client

        logger.info("Building/Loading RAG vectorstore from docs/...")
        app.state.vectordb = create_rag()
        logger.info("RAG vectorstore ready")
    except Exception:
        logger.exception("Error during startup initialization")
        raise


class ChatRequest(BaseModel):
    message: str
    username: str = "guest"


class ChallengeLogRequest(BaseModel):
    username: str
    carbon_saved: float
    activity: str


class ReminderRequest(BaseModel):
    username: str
    habit: str
    frequency: str  # daily, weekly, etc.


# Optional carbon calculator
def calculate_carbon(msg):
    msg = msg.lower()
    if "bottle" in msg or "plastic" in msg:
        return 1
    if "cycle" in msg or "bike" in msg:
        return 3
    if "tree" in msg:
        return 2
    if "light" in msg:
        return 1
    if "bus" in msg or "train" in msg:
        return 2
    if "meat" in msg:
        return 3
    return 0


@app.post("/chat")
def chat(req: ChatRequest, request: Request):
    try:
        user_message = req.message
        # RAG search for context
        vectordb = request.app.state.vectordb
        docs = vectordb.similarity_search(user_message, k=3)
        context = "\n".join([d.page_content for d in docs])

        prompt = f"""You are a sustainability coach.
Use this knowledge to help the user.

Knowledge:
{context}

User: {user_message}
"""

        client = request.app.state.client
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )

        reply = response.choices[0].message.content
        carbon = calculate_carbon(user_message)

        return {"reply": reply, "carbon_saved": carbon}

    except Exception as e:
        return {"error": str(e)}


# Daily challenges - same for all users
DAILY_CHALLENGES = [
    {
        "id": 1,
        "title": "Use Public Transport",
        "description": "Take the bus or train instead of driving",
        "carbon_value": 5,
        "category": "Transport",
    },
    {
        "id": 2,
        "title": "Plant a Tree",
        "description": "Plant a tree in your area",
        "carbon_value": 10,
        "category": "Nature",
    },
    {
        "id": 3,
        "title": "Reduce Meat",
        "description": "Go vegetarian for one meal",
        "carbon_value": 3,
        "category": "Diet",
    },
    {
        "id": 4,
        "title": "Save Water",
        "description": "Take a shorter shower",
        "carbon_value": 2,
        "category": "Water",
    },
    {
        "id": 5,
        "title": "Use Reusable Bags",
        "description": "Shop with reusable bags",
        "carbon_value": 1,
        "category": "Waste",
    },
]


@app.get("/challenge/daily")
def get_daily_challenge():
    """Get today's challenge - SAME FOR ALL USERS"""
    from datetime import date
    import hashlib

    # Use date hash to pick the same challenge for everyone
    today = str(date.today())
    hash_value = int(hashlib.md5(today.encode()).hexdigest(), 16)
    challenge_index = hash_value % len(DAILY_CHALLENGES)

    challenge = DAILY_CHALLENGES[challenge_index]
    return challenge


@app.get("/leaderboard")
def get_leaderboard_endpoint():
    """Get top 10 users by carbon saved"""
    return get_leaderboard(10)


@app.post("/carbon/log")
def log_carbon_endpoint(req: ChallengeLogRequest):
    """Log carbon saved for a user"""
    try:
        user = get_user(req.username)
        if not user:
            user_id = create_user(req.username)
        else:
            user_id = user["id"]

        log_carbon(user_id, req.carbon_saved, req.activity)
        return {
            "message": "Carbon saved logged!",
            "username": req.username,
            "carbon_saved": req.carbon_saved,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/user/{username}")
def get_user_stats(username: str):
    """Get user statistics"""
    try:
        user = get_user(username)
        if not user:
            return {"error": "User not found"}
        return user
    except Exception as e:
        return {"error": str(e)}


@app.post("/reminder/add")
def add_reminder_endpoint(req: ReminderRequest):
    """Add a reminder for a user"""
    try:
        user = get_user(req.username)
        if not user:
            user_id = create_user(req.username)
        else:
            user_id = user["id"]

        add_reminder(user_id, req.habit, req.frequency)
        return {"message": f"Reminder added: {req.habit}"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/reminders/{username}")
def get_reminders_endpoint(username: str):
    """Get all reminders for a user"""
    try:
        user = get_user(username)
        if not user:
            return {"error": "User not found"}

        reminders = get_user_reminders(user["id"])
        return reminders
    except Exception as e:
        return {"error": str(e)}


@app.post("/rebuild-rag")
def rebuild_rag_endpoint(x_rebuild_token: str = Header(None), request: Request = None):
    """Trigger a rebuild of the RAG vector DB from the `backend/docs/` folder.

    This deletes the persisted `./db` directory and re-indexes documents.
    """
    # protect with simple token
    REBUILD_TOKEN = os.getenv("REBUILD_TOKEN")
    if REBUILD_TOKEN and x_rebuild_token != REBUILD_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        new_db = rebuild_rag()
        # update running state
        request.app.state.vectordb = new_db
        logger.info("RAG rebuilt and vectordb updated")
        return {"message": "RAG rebuilt successfully"}
    except Exception as e:
        logger.exception("Error rebuilding RAG")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
