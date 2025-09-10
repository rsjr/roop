"""Pydantic schemas for task operations - simplified and clean."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    """Schema for creating a task."""

    name: str = Field(..., min_length=1, max_length=255, description="Task name")
    wave_height_limit: float = Field(
        ..., ge=0, description="Maximum acceptable wave height in meters"
    )
    duration_hours: float = Field(
        4.0, gt=0, le=168, description="Task duration in hours"
    )
    predecessor_id: int | None = Field(None, description="ID of predecessor task")


class TaskResponse(BaseModel):
    """Schema for task responses."""

    id: int
    name: str
    status: TaskStatus
    wave_height_limit: float
    duration_hours: float
    predecessor_id: int | None
    created_at: datetime
    can_start: bool
    should_be_blocked: bool

    class Config:
        from_attributes = True


class TasksCreateRequest(BaseModel):
    """Schema for creating multiple tasks."""

    tasks: list[TaskCreate] = Field(
        ..., min_items=1, description="List of tasks to create"
    )


class TasksCreateResponse(BaseModel):
    """Schema for multiple task creation response."""

    created_tasks: list[TaskResponse]
    total_created: int


class ScheduleStatusResponse(BaseModel):
    """Schema for schedule status response."""

    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    ready_tasks: int
    blocked_tasks: int
    completion_percentage: float
    next_available_task: TaskResponse | None = None
