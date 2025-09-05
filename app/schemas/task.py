"""Pydantic schemas for task operations."""

from typing import Optional

from pydantic import Field, validator

from app.models.task import TaskStatus
from app.schemas.base import BaseSchema, TimestampMixin


class TaskBase(BaseSchema):
    """Base task schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Task name")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    duration_hours: float = Field(..., gt=0, le=168, description="Task duration in hours")
    wave_height_limit: float = Field(..., ge=0, description="Maximum acceptable wave height in meters")
    
    @validator("duration_hours")
    def validate_duration(cls, v: float) -> float:
        """Validate duration is reasonable."""
        if v <= 0:
            raise ValueError("Duration must be positive")
        if v > 168:  # 1 week
            raise ValueError("Duration cannot exceed 168 hours (1 week)")
        return round(v, 2)


class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    
    predecessor_id: Optional[int] = Field(None, description="ID of predecessor task")


class TaskUpdate(BaseSchema):
    """Schema for updating an existing task."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Task name")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    duration_hours: Optional[float] = Field(None, gt=0, le=168, description="Task duration in hours")
    wave_height_limit: Optional[float] = Field(None, ge=0, description="Maximum acceptable wave height")
    predecessor_id: Optional[int] = Field(None, description="ID of predecessor task")


class TaskStatusUpdate(BaseSchema):
    """Schema for updating task status."""
    
    status: TaskStatus = Field(..., description="New task status")


class TaskResponse(TaskBase, TimestampMixin):
    """Schema for task responses."""
    
    id: int = Field(..., description="Task ID")
    status: TaskStatus = Field(..., description="Current task status")
    predecessor_id: Optional[int] = Field(None, description="ID of predecessor task")
    
    # Computed properties
    can_start: bool = Field(..., description="Whether task can be started now")
    is_blocked: bool = Field(..., description="Whether task is blocked by dependencies")
    duration_data_points: int = Field(..., description="Duration in 30-minute data points")


class TaskScheduleResponse(BaseSchema):
    """Response schema for full schedule."""
    
    tasks: list[TaskResponse] = Field(..., description="All tasks in the schedule")
    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    ready_tasks: int = Field(..., description="Number of ready tasks")
    next_task: Optional[TaskResponse] = Field(None, description="Next task to be executed")
    blocks: list[int] = Field(default_factory=list, description="List of successor task IDs")
    can_run_in_parallel: list[int] = Field(default_factory=list, description="Tasks that can run in parallel")


class ScheduleValidationResult(BaseSchema):
    """Result of schedule validation."""
    
    is_valid: bool = Field(..., description="Whether the schedule is valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")
    circular_dependencies: list[list[int]] = Field(
        default_factory=list, 
        description="Circular dependency chains found"
    )
    orphaned_tasks: list[int] = Field(
        default_factory=list, 
        description="Tasks with missing predecessors"
    )