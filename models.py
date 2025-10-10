from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    github_username = Column(String)
    github_access_token = Column(Text)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tasks = relationship("Task", back_populates="owner")
    pomodoro_sessions = relationship("PomodoroSession", back_populates="owner")
    github_stats = relationship("GitHubStats", back_populates="owner")
    ai_insights = relationship("AIInsight", back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(String, default="medium")  # low, medium, high
    completed = Column(Boolean, default=False)
    deadline = Column(DateTime(timezone=True))
    time_spent = Column(Integer, default=0)  # in minutes
    tags = Column(Text)  # JSON string for tags array
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="tasks")
    pomodoro_sessions = relationship("PomodoroSession", back_populates="task")

class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    duration = Column(Integer, nullable=False)  # in minutes
    completed = Column(Boolean, default=False)
    session_type = Column(String, default="work")  # work, break
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    owner = relationship("User", back_populates="pomodoro_sessions")
    task = relationship("Task", back_populates="pomodoro_sessions")

class GitHubStats(Base):
    __tablename__ = "github_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    commits = Column(Integer, default=0)
    lines_added = Column(Integer, default=0)
    lines_removed = Column(Integer, default=0)
    pull_requests = Column(Integer, default=0)
    issues = Column(Integer, default=0)
    repositories = Column(Text)  # JSON string for repository array
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="github_stats")

class AIInsight(Base):
    __tablename__ = "ai_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # peak_hours, focus_trend, break_reminder
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    confidence = Column(Integer, default=80)  # 0-100
    actionable = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="ai_insights")