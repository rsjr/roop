"""Task management service with dependency logic."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus


class TaskService:
    """Service for managing tasks and their dependencies."""

    async def _check_task_should_be_blocked(self, task: Task, db: AsyncSession) -> bool:
        """Check if a task should be blocked based on its predecessor."""
        if task.predecessor_id is None:
            return False

        # Get the predecessor task
        result = await db.execute(select(Task).where(Task.id == task.predecessor_id))
        predecessor = result.scalar_one_or_none()

        if not predecessor:
            return False

        # Task should be blocked if predecessor is not completed
        return predecessor.status != TaskStatus.COMPLETED

    async def _check_task_can_start(self, task: Task, db: AsyncSession) -> bool:
        """Check if a task can be started."""
        # Task can start if it's not blocked by dependencies
        is_blocked = await self._check_task_should_be_blocked(task, db)
        return not is_blocked and task.status == TaskStatus.READY

    async def update_task_statuses(self, db: AsyncSession) -> None:
        """Update all task statuses based on dependencies."""
        # Get all tasks
        result = await db.execute(select(Task))
        tasks = result.scalars().all()

        for task in tasks:
            if task.status in [TaskStatus.COMPLETED, TaskStatus.IN_PROGRESS]:
                # Don't change completed or in-progress tasks
                continue

            # Check if task should be blocked or ready
            should_be_blocked = await self._check_task_should_be_blocked(task, db)

            if should_be_blocked and task.status != TaskStatus.BLOCKED:
                task.status = TaskStatus.BLOCKED
            elif not should_be_blocked and task.status == TaskStatus.BLOCKED:
                task.status = TaskStatus.READY

        await db.commit()

    async def complete_task(self, task_id: int, db: AsyncSession) -> Task:
        """Mark a task as completed and update dependent tasks."""
        # Get the task
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        if task.status not in [TaskStatus.READY, TaskStatus.IN_PROGRESS]:
            raise ValueError(
                f"Task {task_id} cannot be completed from status {task.status}"
            )

        # Mark as completed
        task.status = TaskStatus.COMPLETED
        await db.commit()

        # Update all task statuses to handle newly unblocked tasks
        await self.update_task_statuses(db)

        return task

    async def start_task(self, task_id: int, db: AsyncSession) -> Task:
        """Mark a task as in progress if dependencies are met."""
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Check if task can be started
        can_start = await self._check_task_can_start(task, db)

        if not can_start:
            raise ValueError(
                f"Task {task_id} cannot be started - dependencies not met or not in READY status"
            )

        task.status = TaskStatus.IN_PROGRESS
        await db.commit()

        return task

    async def get_schedule_status(self, db: AsyncSession) -> dict:
        """Get overview of schedule status."""
        result = await db.execute(select(Task))
        tasks = result.scalars().all()

        # Count tasks by status
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        in_progress_tasks = sum(1 for t in tasks if t.status == TaskStatus.IN_PROGRESS)
        ready_tasks = sum(1 for t in tasks if t.status == TaskStatus.READY)
        blocked_tasks = sum(1 for t in tasks if t.status == TaskStatus.BLOCKED)

        # Find next ready task
        next_ready_task = None
        for task in tasks:
            if task.status == TaskStatus.READY:
                next_ready_task = task
                break

        completion_percentage = (completed_tasks / len(tasks) * 100) if tasks else 0

        return {
            "total_tasks": len(tasks),
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "ready_tasks": ready_tasks,
            "blocked_tasks": blocked_tasks,
            "completion_percentage": round(completion_percentage, 2),
            "next_available_task": next_ready_task,
        }


# Global task service instance
task_service = TaskService()
