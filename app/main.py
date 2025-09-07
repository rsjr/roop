"""Marine Operations FastAPI application with SQLAlchemy."""

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.task import Task, TaskStatus

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


@app.post("/tasks")
async def create_task(
    name: str, wave_height_limit: float, db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    task = Task(name=name, wave_height_limit=wave_height_limit, status=TaskStatus.READY)
    db.add(task)
    await db.commit()
    await db.refresh(task)

    return {
        "id": task.id,
        "name": task.name,
        "status": task.status,
        "wave_height_limit": task.wave_height_limit,
        "created_at": task.created_at,
    }


@app.get("/tasks")
async def get_tasks(db: AsyncSession = Depends(get_db)):
    """Get all tasks."""
    result = await db.execute(select(Task).order_by(Task.id))
    tasks = result.scalars().all()

    return {
        "tasks": [
            {
                "id": task.id,
                "name": task.name,
                "status": task.status,
                "wave_height_limit": task.wave_height_limit,
                "created_at": task.created_at,
            }
            for task in tasks
        ]
    }


@app.get("/tasks/{task_id}")
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": task.id,
        "name": task.name,
        "status": task.status,
        "wave_height_limit": task.wave_height_limit,
        "created_at": task.created_at,
    }


@app.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: int, status: TaskStatus, db: AsyncSession = Depends(get_db)
):
    """Update task status."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = status
    await db.commit()
    await db.refresh(task)

    return {
        "id": task.id,
        "name": task.name,
        "status": task.status,
        "wave_height_limit": task.wave_height_limit,
        "created_at": task.created_at,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
