from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
import json

from database import get_db
from models import GitHubStats, User
from auth_utils import get_current_user

router = APIRouter()

class GitHubStatsResponse(BaseModel):
    id: int
    date: datetime
    commits: int
    lines_added: int
    lines_removed: int
    pull_requests: int
    issues: int
    repositories: List[str]

    class Config:
        from_attributes = True

@router.get("/stats", response_model=List[GitHubStatsResponse])
async def get_github_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(GitHubStats).filter(GitHubStats.user_id == current_user.id)
    
    if start_date:
        query = query.filter(GitHubStats.date >= start_date)
    if end_date:
        query = query.filter(GitHubStats.date <= end_date)
    
    stats = query.order_by(GitHubStats.date.desc()).all()
    
    # Parse repositories from JSON string
    for stat in stats:
        if stat.repositories:
            try:
                stat.repositories = json.loads(stat.repositories)
            except:
                stat.repositories = []
        else:
            stat.repositories = []
    
    return stats

@router.post("/sync")
async def sync_github_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    This endpoint would normally fetch data from GitHub API
    For now, it creates sample data
    """
    from datetime import timedelta
    import random
    
    # Generate sample data for the last 30 days
    today = datetime.now().date()
    for i in range(30):
        stat_date = today - timedelta(days=i)
        
        # Check if we already have data for this date
        existing = db.query(GitHubStats).filter(
            GitHubStats.user_id == current_user.id,
            GitHubStats.date == stat_date
        ).first()
        
        if not existing:
            # Create sample data
            stat = GitHubStats(
                user_id=current_user.id,
                date=stat_date,
                commits=random.randint(0, 10),
                lines_added=random.randint(0, 500),
                lines_removed=random.randint(0, 200),
                pull_requests=random.randint(0, 3),
                issues=random.randint(0, 2),
                repositories=json.dumps(["project-1", "project-2"])
            )
            db.add(stat)
    
    db.commit()
    return {"message": "GitHub data synced successfully"}