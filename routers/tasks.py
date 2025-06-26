from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

from database import get_db
from models import Task, User
from auth_utils import get_current_user

router = APIRouter()

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    deadline: Optional[datetime] = None
    tags: Optional[List[str]] = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None
    deadline: Optional[datetime] = None
    tags: Optional[List[str]] = None
    time_spent: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    deadline: Optional[datetime]
    time_spent: int
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).order_by(Task.created_at.desc()).all()
    
    # Parse tags from JSON string
    for task in tasks:
        if task.tags:
            try:
                task.tags = json.loads(task.tags)
            except:
                task.tags = []
        else:
            task.tags = []
    
    return tasks

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    db_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        deadline=task.deadline,
        tags=json.dumps(task.tags) if task.tags else None,
        user_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Parse tags for response
    if db_task.tags:
        try:
            db_task.tags = json.loads(db_task.tags)
        except:
            db_task.tags = []
    else:
        db_task.tags = []
    
    return db_task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    
    # Handle tags conversion
    if "tags" in update_data:
        update_data["tags"] = json.dumps(update_data["tags"]) if update_data["tags"] else None
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    
    # Parse tags for response
    if db_task.tags:
        try:
            db_task.tags = json.loads(db_task.tags)
        except:
            db_task.tags = []
    else:
        db_task.tags = []
    
    return db_task

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    
    return {"message": "Task deleted successfully"}