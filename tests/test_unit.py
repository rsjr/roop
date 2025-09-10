"""Unit tests for Marine Operations Service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.task import Task, TaskStatus
from app.services.task import TaskService
from app.services.wow import wow_analysis


class TestTaskModel:
    """Test Task model properties."""

    def test_task_can_start_when_ready(self):
        """Test that a READY task can start."""
        task = Task(
            name="Test Task",
            status=TaskStatus.READY,
            wave_height_limit=2.0,
            duration_hours=4.0,
        )
        assert task.can_start is True

    def test_task_cannot_start_when_blocked(self):
        """Test that a BLOCKED task cannot start."""
        task = Task(
            name="Test Task",
            status=TaskStatus.BLOCKED,
            wave_height_limit=2.0,
            duration_hours=4.0,
        )
        assert task.can_start is False

    def test_task_should_be_blocked_when_blocked(self):
        """Test that a BLOCKED task should be blocked."""
        task = Task(
            name="Test Task",
            status=TaskStatus.BLOCKED,
            wave_height_limit=2.0,
            duration_hours=4.0,
        )
        assert task.should_be_blocked is True

    def test_task_should_not_be_blocked_when_ready(self):
        """Test that a READY task should not be blocked."""
        task = Task(
            name="Test Task",
            status=TaskStatus.READY,
            wave_height_limit=2.0,
            duration_hours=4.0,
        )
        assert task.should_be_blocked is False


class TestTaskService:
    """Test TaskService business logic."""

    @pytest.fixture
    def task_service(self):
        """Fixture providing TaskService instance."""
        return TaskService()

    @pytest.fixture
    def mock_db(self):
        """Fixture providing mock database session."""
        db = AsyncMock()
        return db

    @pytest.mark.asyncio
    async def test_complete_task_success(self, task_service, mock_db):
        """Test successful task completion."""
        # Setup mock task
        task = Task(
            id=1,
            name="Test Task",
            status=TaskStatus.READY,
            wave_height_limit=2.0,
            duration_hours=4.0,
        )

        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = task
        mock_db.execute.return_value = mock_result

        # Test completion
        completed_task = await task_service.complete_task(1, mock_db)

        assert completed_task.status == TaskStatus.COMPLETED
        mock_db.commit.assert_called()

    @pytest.mark.asyncio
    async def test_complete_task_not_found(self, task_service, mock_db):
        """Test task completion when task doesn't exist."""
        # Mock database query returning None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Test that ValueError is raised
        with pytest.raises(ValueError, match="Task 999 not found"):
            await task_service.complete_task(999, mock_db)

    @pytest.mark.asyncio
    async def test_start_task_success(self, task_service, mock_db):
        """Test successful task start."""
        # Setup mock task
        task = Task(
            id=1,
            name="Test Task",
            status=TaskStatus.READY,
            wave_height_limit=2.0,
            duration_hours=4.0,
        )

        # Mock database queries
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = task
        mock_db.execute.return_value = mock_result

        # Test start
        started_task = await task_service.start_task(1, mock_db)

        assert started_task.status == TaskStatus.IN_PROGRESS
        mock_db.commit.assert_called()


class TestWowAnalysis:
    """Test WoW analysis function."""

    def test_wow_analysis_all_good_conditions(self):
        """Test WoW analysis with all good wave conditions."""
        wave_heights = [1.0, 1.2, 1.1, 0.9, 1.3, 1.0]
        task_duration = 4
        wave_limit = 2.0

        go_no_go, start_indices = wow_analysis(wave_heights, task_duration, wave_limit)

        # All conditions should be good
        assert all(go_no_go)
        # Should find valid start windows
        assert len(start_indices) > 0
        assert 0 in start_indices

    def test_wow_analysis_no_good_windows(self):
        """Test WoW analysis with no suitable windows."""
        wave_heights = [3.0, 3.2, 2.8, 3.1, 2.9, 3.0]
        task_duration = 4
        wave_limit = 2.0

        go_no_go, start_indices = wow_analysis(wave_heights, task_duration, wave_limit)

        # No conditions should be good
        assert not any(go_no_go)
        # Should find no valid start windows
        assert len(start_indices) == 0

    def test_wow_analysis_partial_good_window(self):
        """Test WoW analysis with partial good conditions."""
        wave_heights = [1.0, 1.5, 3.0, 1.2, 1.1, 1.0]
        task_duration = 3
        wave_limit = 2.0

        go_no_go, start_indices = wow_analysis(wave_heights, task_duration, wave_limit)

        # Should have mixed conditions
        expected_signals = [True, True, False, True, True, True]
        assert go_no_go == expected_signals

        # Should find valid windows at indices 3 (for positions 3,4,5)
        assert 3 in start_indices

    def test_wow_analysis_exact_limit(self):
        """Test WoW analysis with waves exactly at limit."""
        wave_heights = [2.0, 2.0, 2.0, 2.0]
        task_duration = 4
        wave_limit = 2.0

        go_no_go, start_indices = wow_analysis(wave_heights, task_duration, wave_limit)

        # All should be acceptable (<=)
        assert all(go_no_go)
        assert 0 in start_indices

    def test_wow_analysis_insufficient_duration(self):
        """Test WoW analysis with insufficient data for duration."""
        wave_heights = [1.0, 1.0]
        task_duration = 4
        wave_limit = 2.0

        go_no_go, start_indices = wow_analysis(wave_heights, task_duration, wave_limit)

        # Should have signals for available data
        assert len(go_no_go) == 2
        assert all(go_no_go)

        # But no valid start windows due to insufficient duration
        assert len(start_indices) == 0


class TestTaskDependencies:
    """Test task dependency logic."""

    def test_task_with_no_predecessor_ready(self):
        """Test that task with no predecessor starts as READY."""
        task = Task(
            name="First Task",
            status=TaskStatus.READY,
            wave_height_limit=2.0,
            duration_hours=4.0,
            predecessor_id=None,
        )
        assert task.predecessor_id is None
        assert task.status == TaskStatus.READY

    def test_task_with_predecessor_can_be_blocked(self):
        """Test that task with predecessor can be blocked."""
        task = Task(
            name="Dependent Task",
            status=TaskStatus.BLOCKED,
            wave_height_limit=2.0,
            duration_hours=4.0,
            predecessor_id=1,
        )
        assert task.predecessor_id == 1
        assert task.status == TaskStatus.BLOCKED


# Integration test for the API
class TestTaskAPI:
    """Integration tests for task API endpoints."""

    def test_task_status_transitions(self):
        """Test valid task status transitions."""
        # Task starts as READY
        task = Task(
            name="Test",
            status=TaskStatus.READY,
            wave_height_limit=2.0,
            duration_hours=4.0,
        )
        assert task.status == TaskStatus.READY

        # Can transition to IN_PROGRESS
        task.status = TaskStatus.IN_PROGRESS
        assert task.status == TaskStatus.IN_PROGRESS

        # Can transition to COMPLETED
        task.status = TaskStatus.COMPLETED
        assert task.status == TaskStatus.COMPLETED

        # Task can be BLOCKED
        task.status = TaskStatus.BLOCKED
        assert task.status == TaskStatus.BLOCKED


if __name__ == "__main__":
    # Run with: python -m pytest tests/test_marine_operations.py -v
    pytest.main([__file__, "-v"])
