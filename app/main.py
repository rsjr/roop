from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskResponse, TasksCreateRequest, TasksCreateResponse
from app.schemas.weather import WeatherForecast
from app.services.task import task_service
from app.services.weather import weather_service
from app.services.wow import wow_service

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

# =============================================================================
# TASK ENDPOINTS
# =============================================================================


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Marine Operations Service",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


# =============================================================================
# TASK ENDPOINTS
# =============================================================================


@app.post("/tasks", response_model=TasksCreateResponse)
async def create_tasks(request: TasksCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create one or more tasks with dependencies."""
    created_tasks = []

    for task_data in request.tasks:
        # Validate predecessor exists if specified
        if task_data.predecessor_id is not None:
            pred_result = await db.execute(
                select(Task).where(Task.id == task_data.predecessor_id)
            )
            predecessor = pred_result.scalar_one_or_none()
            if not predecessor:
                raise HTTPException(
                    status_code=400,
                    detail=f"Predecessor task {task_data.predecessor_id} not found",
                )

        task = Task(
            name=task_data.name,
            wave_height_limit=task_data.wave_height_limit,
            duration_hours=task_data.duration_hours,
            predecessor_id=task_data.predecessor_id,
            status=TaskStatus.READY,
        )
        db.add(task)
        created_tasks.append(task)

    await db.commit()

    # Refresh all tasks to get the IDs and timestamps
    for task in created_tasks:
        await db.refresh(task)

    # Update task statuses based on dependencies
    await task_service.update_task_statuses(db)

    # Refresh again to get updated statuses
    for task in created_tasks:
        await db.refresh(task)

    return TasksCreateResponse(
        created_tasks=[TaskResponse.model_validate(task) for task in created_tasks],
        total_created=len(created_tasks),
    )


@app.get("/tasks")
async def get_tasks(db: AsyncSession = Depends(get_db)):
    """Get all tasks with dependency information."""
    result = await db.execute(select(Task).order_by(Task.id))
    tasks = result.scalars().all()

    return {"tasks": [TaskResponse.model_validate(task) for task in tasks]}


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse.model_validate(task)


@app.put("/tasks/{task_id}/complete")
async def complete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Mark a task as completed and update dependent tasks."""
    try:
        task = await task_service.complete_task(task_id, db)
        await db.refresh(task)
        return {
            "message": f"Task {task_id} completed",
            "task": TaskResponse.model_validate(task),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/tasks/{task_id}/start")
async def start_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Mark a task as started (in progress)."""
    try:
        task = await task_service.start_task(task_id, db)
        await db.refresh(task)
        return {
            "message": f"Task {task_id} started",
            "task": TaskResponse.model_validate(task),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/schedule/status")
async def get_schedule_status(db: AsyncSession = Depends(get_db)):
    """Get overall schedule status."""
    return await task_service.get_schedule_status(db)


# =============================================================================
# WEATHER ENDPOINTS
# =============================================================================


@app.get("/weather", response_model=WeatherForecast)
async def get_weather_forecast(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    from_time: datetime = Query(None, description="Start time (ISO format)"),
    to_time: datetime = Query(None, description="End time (ISO format)"),
):
    """Get weather forecast for a location and time range."""
    return await weather_service.get_forecast(lat, lon, from_time, to_time)


@app.get("/weather/12h", response_model=WeatherForecast)
async def get_12_hour_forecast(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
):
    """Get 12-hour weather forecast."""
    return await weather_service.get_12_hour_forecast(lat, lon)


# =============================================================================
# WOW ANALYSIS ENDPOINTS
# =============================================================================


@app.post("/wow/analyze")
async def analyze_wow(
    task_id: int = Query(..., description="Task ID to analyze"),
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    forecast_hours: int = Query(
        12, ge=1, le=168, description="Forecast hours to analyze"
    ),
    db: AsyncSession = Depends(get_db),
):
    """Perform Wait on Weather (WoW) analysis for a task."""
    # Get the task
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status not in [TaskStatus.READY, TaskStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=400,
            detail=f"Task must be READY or IN_PROGRESS for analysis. Current status: {task.status}",
        )

    # Perform WoW analysis
    analysis_result = await wow_service.analyze_task(task, lat, lon, forecast_hours)

    return analysis_result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
