"""Task model for marine operations schedule."""

from enum import Enum
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin


class TaskStatus(str, Enum):
    """Task status enumeration."""

    READY = "READY"
    IN_PROGRESS = "IN_PROGRESS" 
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"


class Task(Base, TimestampMixin):
    """Task model representing a marine operation sub-task."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Duration in hours
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Task dependencies
    predecessor_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("tasks.id"), nullable=True, index=True
    )
    
    # Task status
    status: Mapped[TaskStatus] = mapped_column(
        String(20), nullable=False, default=TaskStatus.READY, index=True
    )
    
    # Weather constraints
    wave_height_limit: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    predecessor: Mapped[Optional["Task"]] = relationship(
        "Task", remote_side=[id], back_populates="successors"
    )
    successors: Mapped[list["Task"]] = relationship(
        "Task", back_populates="predecessor"
    )

    def __repr__(self) -> str:
        """String representation of task."""
        return f"<Task(id={self.id}, name='{self.name}', status='{self.status}')>"

    @property
    def duration_data_points(self) -> int:
        """
        Convert duration from hours to data points.
        Assuming weather data is provided every 30 minutes.
        """
        return int(self.duration_hours * 2)

    def can_start(self) -> bool:
        """Check if task can be started based on status and dependencies."""
        if self.status != TaskStatus.READY:
            return False
        
        if self.predecessor_id is None:
            return True
            
        return (
            self.predecessor is not None 
            and self.predecessor.status == TaskStatus.COMPLETED
        )

    def is_blocked(self) -> bool:
        """Check if task is blocked by dependencies."""
        if self.predecessor_id is None:
            return False
            
        return (
            self.predecessor is None 
            or self.predecessor.status != TaskStatus.COMPLETED
        )