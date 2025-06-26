from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import PomodoroSession, User
from auth_utils import get_current_user

router = APIRouter()

class PomodoroCreate(BaseModel):
    duration: int  # in minutes
    session_type: str = "work"
    task_id: Optional[int] = None

class PomodoroUpdate(BaseModel):
    completed: Optional[bool] = None
    completed_at: Optional[datetime] = None

class PomodoroResponse(BaseModel):
    id: int
    duration: int
    completed: bool
    session_type: str
    task_id: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.get("/sessions", response_model=List[PomodoroResponse])
async def get_sessions(
    limit: int = 50,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    sessions = db.query(PomodoroSession).filter(
        PomodoroSession.user_id == current_user.id
    ).order_by(PomodoroSession.started_at.desc()).limit(limit).all()
    return sessions

@router.post("/sessions", response_model=PomodoroResponse)
async def create_session(
    session: PomodoroCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_session = PomodoroSession(
        duration=session.duration,
        session_type=session.session_type,
        task_id=session.task_id,
        user_id=current_user.id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.put("/sessions/{session_id}", response_model=PomodoroResponse)
async def update_session(
    session_id: int,
    session_update: PomodoroUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_session = db.query(PomodoroSession).filter(
        PomodoroSession.id == session_id,
        PomodoroSession.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_data = session_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session