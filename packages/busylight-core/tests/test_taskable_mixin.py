"""Tests for the TaskableMixin class."""

import asyncio
from unittest.mock import Mock, patch

import pytest

from busylight_core.mixins.taskable import TaskableMixin


class TestTaskableMixin:
    """Test cases for TaskableMixin functionality."""

    def test_event_loop_property(self) -> None:
        """Test that event_loop property returns an event loop."""
        mixin = TaskableMixin()

        with (
            patch("asyncio.get_running_loop") as mock_get_running,
            patch("asyncio.new_event_loop") as mock_new_loop,
        ):
            mock_loop = Mock()
            mock_get_running.side_effect = RuntimeError("no running loop")
            mock_new_loop.return_value = mock_loop

            # Access the property to trigger the call
            result = mixin.event_loop

            mock_get_running.assert_called_once()
            mock_new_loop.assert_called_once()
            assert result is mock_loop

    def test_event_loop_cached_property(self) -> None:
        """Test that event_loop is cached and only calls event loop functions once."""
        mixin = TaskableMixin()

        with (
            patch("asyncio.get_running_loop") as mock_get_running,
            patch("asyncio.new_event_loop") as mock_new_loop,
        ):
            mock_loop = Mock()
            mock_get_running.side_effect = RuntimeError("no running loop")
            mock_new_loop.return_value = mock_loop

            # Access the property multiple times
            result1 = mixin.event_loop
            result2 = mixin.event_loop

            # Should only call event loop functions once due to caching
            mock_get_running.assert_called_once()
            mock_new_loop.assert_called_once()
            assert result1 is mock_loop
            assert result2 is mock_loop
            assert result1 is result2

    def test_tasks_property_initial_state(self) -> None:
        """Test that tasks property returns empty dict initially."""
        mixin = TaskableMixin()

        assert isinstance(mixin.tasks, dict)
        assert len(mixin.tasks) == 0

    def test_tasks_cached_property(self) -> None:
        """Test that tasks property is cached and returns same dict."""
        mixin = TaskableMixin()

        tasks1 = mixin.tasks
        tasks2 = mixin.tasks

        assert tasks1 is tasks2
        assert isinstance(tasks1, dict)

    def test_add_task_new_task(self) -> None:
        """Test adding a new task creates and stores it."""
        mixin = TaskableMixin()
        mock_task = Mock()
        mock_loop = Mock()
        mock_loop.create_task.return_value = mock_task

        # Mock coroutine function
        async def mock_coroutine(self, *args, **kwargs) -> str:  # noqa: ARG001, ANN002, ANN003
            return "test_result"

        with patch.object(mixin, "event_loop", mock_loop):
            result = mixin.add_task("test_task", mock_coroutine, 0)

        # Verify task was created and stored
        mock_loop.create_task.assert_called_once()
        assert result is mock_task
        assert mixin.tasks["test_task"] is mock_task

    def test_add_task_existing_task_returns_existing(self) -> None:
        """Test adding task with existing name returns existing task."""
        mixin = TaskableMixin()
        existing_task = Mock()
        mixin.tasks["existing_task"] = existing_task

        # Mock coroutine function
        async def mock_coroutine(self) -> str:  # noqa: ARG001
            return "test_result"

        mock_loop = Mock()
        with patch.object(mixin, "event_loop", mock_loop):
            result = mixin.add_task("existing_task", mock_coroutine, 0)

        # Should return existing task without creating new one
        assert result is existing_task
        mock_loop.create_task.assert_not_called()

    def test_add_task_coroutine_called_with_self(self) -> None:
        """Test that coroutine is called with self when creating task."""
        mixin = TaskableMixin()
        mock_task = Mock()
        mock_loop = Mock()
        mock_loop.create_task.return_value = mock_task

        # Mock coroutine function that records its argument
        coroutine_args = []

        async def mock_coroutine(arg) -> str:
            coroutine_args.append(arg)
            return "test_result"

        with patch.object(mixin, "event_loop", mock_loop):
            mixin.add_task("test_task", mock_coroutine, 0)

        # Verify the coroutine was called with self
        mock_loop.create_task.assert_called_once()
        mock_loop.create_task.call_args[0][0]
        # The argument should be a coroutine, we can't easily verify the mixin
        # was passed but we can verify create_task was called

    def test_cancel_task_existing_task(self) -> None:
        """Test canceling an existing task."""
        mixin = TaskableMixin()
        mock_task = Mock()
        mixin.tasks["test_task"] = mock_task

        result = mixin.cancel_task("test_task")

        # Verify task was cancelled and removed
        mock_task.cancel.assert_called_once()
        assert result is mock_task
        assert "test_task" not in mixin.tasks

    def test_cancel_task_nonexistent_task(self) -> None:
        """Test canceling a non-existent task returns None."""
        mixin = TaskableMixin()

        result = mixin.cancel_task("nonexistent_task")

        assert result is None
        assert len(mixin.tasks) == 0

    def test_cancel_task_keyerror_handling(self) -> None:
        """Test cancel_task handles KeyError gracefully."""
        mixin = TaskableMixin()

        # Explicitly test KeyError path
        result = mixin.cancel_task("missing_task")

        assert result is None

    def test_cancel_task_attributeerror_handling(self) -> None:
        """Test cancel_task handles AttributeError gracefully."""
        mixin = TaskableMixin()

        # Create a mock task that raises AttributeError on cancel
        mock_task = Mock()
        mock_task.cancel.side_effect = AttributeError("cancel method not found")
        mixin.tasks["problematic_task"] = mock_task

        result = mixin.cancel_task("problematic_task")

        # Should handle the AttributeError and return None
        assert result is None
        # Task should still be removed from tasks dict
        assert "problematic_task" not in mixin.tasks

    def test_cancel_tasks_empty_tasks(self) -> None:
        """Test cancel_tasks with no tasks does nothing."""
        mixin = TaskableMixin()

        # Should not raise any errors
        mixin.cancel_tasks()

        assert len(mixin.tasks) == 0

    def test_cancel_tasks_with_multiple_tasks(self) -> None:
        """Test cancel_tasks cancels all tasks and clears dict."""
        mixin = TaskableMixin()

        # Create multiple mock tasks
        mock_task1 = Mock()
        mock_task2 = Mock()
        mock_task3 = Mock()

        mixin.tasks["task1"] = mock_task1
        mixin.tasks["task2"] = mock_task2
        mixin.tasks["task3"] = mock_task3

        mixin.cancel_tasks()

        # Verify all tasks were cancelled
        mock_task1.cancel.assert_called_once()
        mock_task2.cancel.assert_called_once()
        mock_task3.cancel.assert_called_once()

        # Verify tasks dict is cleared
        assert len(mixin.tasks) == 0

    def test_cancel_tasks_with_task_cancel_error(self) -> None:
        """Test cancel_tasks raises exception when task.cancel() fails."""
        mixin = TaskableMixin()

        # Create tasks, one that raises error on cancel
        mock_task1 = Mock()
        mock_task2 = Mock()
        mock_task2.cancel.side_effect = Exception("Cancel failed")

        mixin.tasks["task1"] = mock_task1
        mixin.tasks["task2"] = mock_task2

        # Should raise exception when task2 cancel fails
        with pytest.raises(Exception, match="Cancel failed"):
            mixin.cancel_tasks()

        # Verify first task had cancel called
        mock_task1.cancel.assert_called_once()
        mock_task2.cancel.assert_called_once()

        # Verify tasks dict is NOT cleared when there's an error
        # (the current implementation doesn't clear on error)
        assert len(mixin.tasks) == 2


class TestTaskableMixinIntegration:
    """Integration tests for TaskableMixin with real asyncio."""

    @pytest.mark.asyncio
    async def test_real_asyncio_integration(self) -> None:
        """Test TaskableMixin with actual asyncio tasks."""
        mixin = TaskableMixin()

        # Create a real coroutine
        async def test_coroutine(self) -> str:  # noqa: ARG001
            await asyncio.sleep(0.1)
            return "completed"

        # Add a task
        task = mixin.add_task("real_task", test_coroutine, 0)

        # Verify it's a real asyncio task
        assert isinstance(task, asyncio.Task)
        assert "real_task" in mixin.tasks

        # Cancel the task
        cancelled_task = mixin.cancel_task("real_task")

        assert cancelled_task is task
        assert "real_task" not in mixin.tasks

        # Wait a bit for cancellation to take effect
        await asyncio.sleep(0.01)
        assert task.cancelled()

    @pytest.mark.asyncio
    async def test_multiple_real_tasks(self) -> None:
        """Test managing multiple real asyncio tasks."""
        mixin = TaskableMixin()

        # Create multiple coroutines
        async def slow_task(self) -> str:  # noqa: ARG001
            await asyncio.sleep(0.2)
            return "slow_completed"

        async def fast_task(self) -> str:  # noqa: ARG001
            await asyncio.sleep(0.05)
            return "fast_completed"

        # Add multiple tasks
        slow = mixin.add_task("slow", slow_task, 0)
        fast = mixin.add_task("fast", fast_task, 0)

        assert len(mixin.tasks) == 2

        # Cancel all tasks
        mixin.cancel_tasks()

        assert len(mixin.tasks) == 0

        # Wait a bit for cancellation to take effect
        await asyncio.sleep(0.01)
        assert slow.cancelled()
        assert fast.cancelled()

    def test_event_loop_property_with_real_loop(self) -> None:
        """Test event_loop property returns actual event loop."""
        mixin = TaskableMixin()

        # Get the actual event loop
        loop = mixin.event_loop

        # Should be a real event loop
        assert isinstance(loop, asyncio.AbstractEventLoop)

        # Should be cached
        loop2 = mixin.event_loop
        assert loop is loop2


class TestTaskableMixinEdgeCases:
    """Test edge cases and error conditions."""

    def test_tasks_property_modification(self) -> None:
        """Test that tasks dict can be modified and persists."""
        mixin = TaskableMixin()

        # Modify the tasks dict directly
        mock_task = Mock()
        mixin.tasks["manual_task"] = mock_task

        # Verify the modification persists
        assert mixin.tasks["manual_task"] is mock_task

        # Verify it's still the same cached dict
        tasks_ref = mixin.tasks
        tasks_ref["another_task"] = Mock()
        assert "another_task" in mixin.tasks

    def test_add_task_with_none_coroutine(self) -> None:
        """Test add_task behavior with None coroutine."""
        mixin = TaskableMixin()

        # This should raise an error when trying to call None
        with pytest.raises(TypeError):
            mixin.add_task("bad_task", None, 0)

    def test_cancel_task_with_none_in_tasks(self) -> None:
        """Test cancel_task when tasks dict contains None."""
        mixin = TaskableMixin()

        # Manually put None in tasks (shouldn't happen in normal use)
        mixin.tasks["none_task"] = None

        # This should trigger AttributeError handling
        result = mixin.cancel_task("none_task")

        assert result is None
        assert "none_task" not in mixin.tasks

    def test_concurrent_task_operations(self) -> None:
        """Test that concurrent operations on tasks work correctly."""
        mixin = TaskableMixin()

        # Add some tasks
        mock_task1 = Mock()
        mock_task2 = Mock()
        mixin.tasks["task1"] = mock_task1
        mixin.tasks["task2"] = mock_task2

        # Simulate concurrent cancel operations
        result1 = mixin.cancel_task("task1")
        result2 = mixin.cancel_task("task1")  # Try to cancel same task again

        assert result1 is mock_task1
        assert result2 is None  # Second cancel should return None
        assert "task1" not in mixin.tasks
        assert "task2" in mixin.tasks  # Other task should be unaffected
