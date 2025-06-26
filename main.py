from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from dotenv import load_dotenv

from database import engine, get_db
from models import Base
from routers import auth, tasks, pomodoro, github, insights
from auth_utils import get_current_user

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevDash API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(pomodoro.router, prefix="/api/pomodoro", tags=["pomodoro"])
app.include_router(github.router, prefix="/api/github", tags=["github"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Dashboard stats endpoint
@app.get("/api/dashboard-stats")
async def get_dashboard_stats(current_user = Depends(get_current_user), db = Depends(get_db)):
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from models import PomodoroSession, Task, GitHubStats
    
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    # Today's focus time
    today_focus = db.query(func.sum(PomodoroSession.duration)).filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.completed == True,
        func.date(PomodoroSession.started_at) == today
    ).scalar() or 0
    
    # Week's focus time
    week_focus = db.query(func.sum(PomodoroSession.duration)).filter(
        PomodoroSession.user_id == current_user.id,
        PomodoroSession.completed == True,
        func.date(PomodoroSession.started_at) >= week_ago
    ).scalar() or 0
    
    # Week's completed tasks
    week_tasks = db.query(func.count(Task.id)).filter(
        Task.user_id == current_user.id,
        Task.completed == True,
        func.date(Task.updated_at) >= week_ago
    ).scalar() or 0
    
    # Today's commits (mock data for now)
    today_commits = 5
    week_commits = 25
    
    return {
        "todayCommits": today_commits,
        "todayFocusTime": round(today_focus / 60, 2) if today_focus else 0,
        "weekCommits": week_commits,
        "weekFocusTime": round(week_focus / 60, 2) if week_focus else 0,
        "weekTasks": week_tasks,
        "streak": 7
    }

# Serve static files in production
if os.getenv("ENVIRONMENT") == "production":
    app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True if os.getenv("ENVIRONMENT") != "production" else False
    )