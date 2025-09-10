"""Task model with computed boolean properties."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskStatus(str, Enum):
    """Task status enumeration."""

    READY = "READY"
    BLOCKED = "BLOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Task(Base):
    """Task model representing a marine operation task."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[TaskStatus] = mapped_column(String, default=TaskStatus.READY)
    wave_height_limit: Mapped[float] = mapped_column(Float, nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)

    # Self-referential foreign key for predecessor
    predecessor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tasks.id"), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    # updated_at: Mapped[Optional[datetime]] = mapped_column(
    #     DateTime,
    #     default=datetime.utcnow,
    #     onupdate=datetime.utcnow
    # )

    # Relationships
    predecessor: Mapped[Optional["Task"]] = relationship(
        "Task", remote_side=[id], back_populates="dependents"
    )

    dependents: Mapped[list["Task"]] = relationship(
        "Task", back_populates="predecessor"
    )

    # Computed properties for Pydantic
    @property
    def can_start(self) -> bool:
        """Whether this task can be started."""
        return self.status == TaskStatus.READY

    @property
    def should_be_blocked(self) -> bool:
        """Whether this task should be blocked."""
        return self.status == TaskStatus.BLOCKED

    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}', status='{self.status}')>"
