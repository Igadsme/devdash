from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import AIInsight, User, PomodoroSession
from auth_utils import get_current_user

router = APIRouter()

class InsightResponse(BaseModel):
    id: int
    type: str
    title: str
    description: str
    confidence: int
    actionable: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[InsightResponse])
async def get_insights(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    insights = db.query(AIInsight).filter(
        AIInsight.user_id == current_user.id
    ).order_by(AIInsight.created_at.desc()).limit(limit).all()
    return insights

@router.post("/generate")
async def generate_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get recent pomodoro sessions for analysis
    sessions = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == current_user.id
    ).order_by(PomodoroSession.started_at.desc()).limit(50).all()
    
    insights = []
    
    if sessions:
        # Analyze peak productivity hours
        hour_counts = {}
        for session in sessions:
            if session.started_at:
                hour = session.started_at.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if hour_counts:
            peak_hour = max(hour_counts.items(), key=lambda x: x[1])
            percentage = round((peak_hour[1] / len(sessions)) * 100)
            
            insight = AIInsight(
                type="peak_hours",
                title="Peak Productivity Hours",
                description=f"You're most productive around {peak_hour[0]}:00 with {percentage}% of your sessions.",
                confidence=85,
                actionable=True,
                user_id=current_user.id
            )
            insights.append(insight)
        
        # Analyze recent focus trends
        recent_sessions = [s for s in sessions[:10] if s.completed]
        if len(recent_sessions) >= 5:
            avg_duration = sum(s.duration for s in recent_sessions) / len(recent_sessions)
            
            if avg_duration > 20:
                insight = AIInsight(
                    type="focus_trend",
                    title="Strong Focus Sessions",
                    description=f"Your average session length is {avg_duration:.1f} minutes. Excellent focus!",
                    confidence=90,
                    actionable=True,
                    user_id=current_user.id
                )
                insights.append(insight)
            else:
                insight = AIInsight(
                    type="focus_trend",
                    title="Consider Longer Sessions",
                    description=f"Your average session is {avg_duration:.1f} minutes. Try extending to 25-minute sessions.",
                    confidence=80,
                    actionable=True,
                    user_id=current_user.id
                )
                insights.append(insight)
        
        # Break pattern analysis
        work_sessions = [s for s in sessions if s.session_type == "work" and s.completed]
        if len(work_sessions) >= 3:
            # Check if user has been working consecutively
            recent_work = work_sessions[:3]
            time_diff = (recent_work[0].started_at - recent_work[2].started_at).total_seconds() / 3600
            
            if time_diff < 3:  # 3 consecutive work sessions within 3 hours
                insight = AIInsight(
                    type="break_reminder",
                    title="Take a Break",
                    description="You've had several focused sessions recently. Consider taking a longer break.",
                    confidence=85,
                    actionable=True,
                    user_id=current_user.id
                )
                insights.append(insight)
    
    # Save insights to database
    for insight in insights:
        db.add(insight)
    
    db.commit()
    
    return {"message": f"Generated {len(insights)} new insights", "count": len(insights)}