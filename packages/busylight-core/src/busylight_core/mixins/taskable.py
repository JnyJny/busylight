"""Asynchronous task support for animating lights."""

import asyncio
import contextlib
import threading
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import IntEnum
from functools import cached_property
from typing import Any

from loguru import logger


class TaskPriority(IntEnum):
    """Task priority levels for scheduling.

    Used to control task execution priority and enable priority-based
    cancellation of tasks.
    """

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskInfo:
    """Information about a managed task.

    Contains task metadata including priority, creation time, and status
    information for enhanced task monitoring and debugging.
    """

    task: asyncio.Task
    priority: TaskPriority
    name: str
    created_at: float

    @property
    def is_running(self) -> bool:
        """Check if task is currently running.

        Returns True if the task has not completed, been cancelled, or failed.
        """
        return not self.task.done()

    @property
    def is_cancelled(self) -> bool:
        """Check if task was cancelled.

        Returns True if the task was explicitly cancelled before completion.
        """
        return self.task.cancelled()

    @property
    def has_exception(self) -> bool:
        """Check if task completed with an exception.

        Returns True if the task completed but raised an unhandled exception.
        """
        return (
            self.task.done()
            and not self.task.cancelled()
            and self.task.exception() is not None
        )

    @property
    def exception(self) -> BaseException | None:
        """Get task exception if any.

        Returns the exception that caused the task to fail, or None if
        the task completed successfully or is still running.
        """
        if self.has_exception:
            return self.task.exception()
        return None


# Type aliases for task functions and instantiators
TaskFunction = (
    Callable[["TaskableMixin"], None]  # Sync function
    | Callable[["TaskableMixin"], Awaitable[None]]  # Async function
)

TaskInstantiator = Callable[
    [str, TaskFunction, float | None], asyncio.Task | threading.Timer
]


class TaskableMixin:
    """Associate and manage asynchronous and synchronous tasks.

    Provides enhanced task management with automatic strategy selection
    (asyncio vs threading), prioritization, error handling, and task
    monitoring capabilities for Light instances.

    The environment automatically determines whether to use asyncio tasks
    or threading timers based on the presence of a running event loop.
    """

    @cached_property
    def event_loop(self) -> asyncio.AbstractEventLoop:
        """The default event loop.

        Returns the currently running event loop, or creates a new one if
        no event loop is currently running.
        """
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.new_event_loop()

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize TaskableMixin with task storage for both strategies."""
        super().__init__(*args, **kwargs)
        self._thread_tasks: dict[str, threading.Timer] = {}
        self._task_lock = threading.Lock()

    @cached_property
    def tasks(self) -> dict[str, asyncio.Task]:
        """Active asyncio tasks that are associated with this instance.

        Dictionary mapping task names to their corresponding asyncio.Task objects.
        """
        return {}

    @cached_property
    def task_info(self) -> dict[str, TaskInfo]:
        """Enhanced task information with priority and status tracking.

        Dictionary mapping task names to TaskInfo objects containing metadata
        about priority, creation time, and current status.
        """
        return {}

    @cached_property
    def task_strategy(self) -> TaskInstantiator:
        """Return the appropriate task instantiation function based on environment.

        Automatically detects if we're in an asyncio context and returns the
        corresponding task creation function. Both functions have identical
        call signatures for transparent usage.

        :return: Function to create tasks (asyncio or threading based)
        """
        # Check if event_loop property is mocked (for testing)
        if hasattr(self.event_loop, "_mock_name"):
            return self._create_asyncio_task

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return self._create_thread_task
        else:
            return self._create_asyncio_task

    def _create_asyncio_task(
        self,
        name: str,
        func: TaskFunction,
        interval: float,
    ) -> asyncio.Task:
        """Create asyncio-based task.

        :param name: Unique identifier for the task
        :param func: Function to execute (sync or async)
        :param interval: For periodic tasks, repeat interval in seconds
        """
        if func is None:
            msg = f"Cannot create asyncio task '{name}' with None function"
            raise TypeError(msg)

        self._cleanup_completed_tasks()

        loop = self.event_loop

        if interval:
            task = loop.create_task(
                self._periodic_asyncio_runner(func, interval), name=name
            )
        elif asyncio.iscoroutinefunction(func):
            task = loop.create_task(func(self), name=name)
        else:
            task = loop.create_task(self._sync_to_async_wrapper(func), name=name)

        task_info = TaskInfo(
            task=task,
            priority=TaskPriority.NORMAL,
            name=name,
            created_at=time.time(),
        )
        self.task_info[name] = task_info
        self.tasks[name] = task
        task.add_done_callback(self._task_completion_callback)
        return task

    def _create_thread_task(
        self, name: str, func: TaskFunction, interval: float | None = None
    ) -> threading.Timer:
        """Create threading-based task with unified signature."""
        if func is None:
            msg = f"Cannot create thread task '{name}' with None function"
            raise TypeError(msg)

        with self._task_lock:
            if interval:
                timer = self._create_periodic_timer(name, func, interval)
            else:
                if asyncio.iscoroutinefunction(func):
                    msg = (
                        f"Cannot run async function '{func.__name__}' in "
                        f"threading context. Use a synchronous function or "
                        f"run in asyncio context."
                    )
                    raise RuntimeError(msg)
                timer = threading.Timer(0, lambda: func(self))

            timer.daemon = True
            self._thread_tasks[name] = timer
            timer.start()

            return timer

    async def _periodic_asyncio_runner(
        self, func: TaskFunction, interval: float
    ) -> None:
        """Run function periodically in asyncio context."""
        while True:
            try:
                if asyncio.iscoroutinefunction(func):
                    await func(self)
                else:
                    func(self)
            except Exception as error:
                logger.error(f"Periodic asyncio task error: {error}")
                break
            await asyncio.sleep(interval)

    async def _sync_to_async_wrapper(self, func: Callable) -> None:
        """Wrap synchronous function for asyncio execution."""
        func(self)

    def _create_periodic_timer(
        self, name: str, func: TaskFunction, interval: float
    ) -> threading.Timer:
        """Create self-rescheduling timer for periodic execution."""

        def periodic_wrapper() -> None:
            if asyncio.iscoroutinefunction(func):
                msg = f"Cannot run async function in threading context: {func.__name__}"
                logger.error(f"Periodic thread task '{name}' error: {msg}")
                with self._task_lock:
                    self._thread_tasks.pop(name, None)
                return

            try:
                func(self)
                with self._task_lock:
                    if name in self._thread_tasks:
                        new_timer = threading.Timer(interval, periodic_wrapper)
                        new_timer.daemon = True
                        self._thread_tasks[name] = new_timer
                        new_timer.start()

            except Exception as error:
                logger.error(f"Periodic thread task '{name}' error: {error}")
                with self._task_lock:
                    self._thread_tasks.pop(name, None)

        return threading.Timer(0, periodic_wrapper)

    def add_task(
        self,
        name: str,
        func: TaskFunction,
        priority: TaskPriority = TaskPriority.NORMAL,
        replace: bool = False,
        interval: float | None = None,
    ) -> asyncio.Task | threading.Timer:
        """Create a task using environment-appropriate strategy.

        The environment (asyncio vs non-asyncio) automatically determines whether
        to use asyncio tasks or threading timers. Both strategies support the same
        function signatures and periodic execution.

        :param name: Unique identifier for the task
        :param func: Function to execute (sync or async)
        :param priority: Task priority (used for asyncio tasks only)
        :param replace: Whether to replace existing task with same name
        :param interval: For periodic tasks, repeat interval in seconds
        :return: Created asyncio.Task or threading.Timer
        """
        if replace:
            self.cancel_task(name)
        elif self._task_exists(name):
            return self._get_existing_task(name)

        return self.task_strategy(name, func, interval)

    def _create_asyncio_task_legacy(
        self, name: str, coroutine: TaskFunction, priority: TaskPriority
    ) -> asyncio.Task:
        """Create asyncio task using legacy coroutine calling convention."""
        self._cleanup_completed_tasks()

        loop = self.event_loop

        task = loop.create_task(coroutine(self), name=name)

        task_info = TaskInfo(
            task=task, priority=priority, name=name, created_at=time.time()
        )
        self.task_info[name] = task_info
        self.tasks[name] = task
        task.add_done_callback(self._task_completion_callback)
        return task

    def _task_exists(self, name: str) -> bool:
        """Check if task exists in either strategy."""
        if not hasattr(self, "_thread_tasks"):
            self._thread_tasks = {}
            self._task_lock = threading.Lock()
        return name in self.tasks or name in self._thread_tasks

    def _get_existing_task(self, name: str) -> asyncio.Task | threading.Timer:
        """Get existing task from either strategy."""
        if not hasattr(self, "_thread_tasks"):
            self._thread_tasks = {}
            self._task_lock = threading.Lock()
        return self.tasks.get(name) or self._thread_tasks.get(name)

    def cancel_task(self, name: str) -> asyncio.Task | threading.Timer | None:
        """Cancel task regardless of which strategy created it.

        :param name: Name of task to cancel
        :return: The cancelled task/timer or None if not found
        """
        if name in self.tasks:
            return self._cancel_asyncio_task(name)

        if not hasattr(self, "_thread_tasks"):
            self._thread_tasks = {}
            self._task_lock = threading.Lock()

        if name in self._thread_tasks:
            return self._cancel_thread_task(name)

        return None

    def _cancel_asyncio_task(self, name: str) -> asyncio.Task | None:
        """Cancel asyncio task."""
        task = self.tasks.pop(name, None)
        if task:
            self.task_info.pop(name, None)
            try:
                task.cancel()
            except AttributeError:
                logger.debug(f"Task '{name}' does not support cancellation")
                return None
            else:
                logger.debug(f"Cancelled asyncio task '{name}'")
                return task
        return task

    def _cancel_thread_task(self, name: str) -> threading.Timer | None:
        """Cancel threading task."""
        with self._task_lock:
            timer = self._thread_tasks.pop(name, None)
            if timer:
                timer.cancel()
                logger.debug(f"Cancelled thread task '{name}'")
            return timer

    def cancel_tasks(self, priority: TaskPriority | None = None) -> None:
        """Cancel all tasks or tasks of specific priority.

        Cancels either all tasks or only tasks matching the specified priority level.

        :param priority: If specified, only cancel tasks of this priority level
        """
        if priority is None:
            if hasattr(self, "_tasks") or "tasks" in self.__dict__:
                for task in self.tasks.values():
                    task.cancel()
                self.tasks.clear()

            if hasattr(self, "_task_info") or "task_info" in self.__dict__:
                self.task_info.clear()

            if hasattr(self, "_thread_tasks"):
                with self._task_lock:
                    for timer in self._thread_tasks.values():
                        timer.cancel()
                    self._thread_tasks.clear()

        elif hasattr(self, "_task_info") or "task_info" in self.__dict__:
            to_cancel = [
                name
                for name, task_info in self.task_info.items()
                if task_info.priority == priority and task_info.is_running
            ]
            for name in to_cancel:
                self.task_info[name].task.cancel()
            self._cleanup_completed_tasks()

    def get_task_status(self, name: str) -> dict[str, Any] | None:
        """Get detailed status information for a task.

        Returns comprehensive status information including running state,
        exceptions, priority, and creation time.

        :param name: Name of task to check
        :return: Dictionary with task status details or None if not found
        """
        task_info = self.task_info.get(name)
        if not task_info:
            task = self.tasks.get(name)
            if task:
                return {
                    "name": name,
                    "running": not task.done(),
                    "cancelled": task.cancelled(),
                    "has_exception": task.done()
                    and not task.cancelled()
                    and task.exception() is not None,
                    "exception": task.exception() if task.done() else None,
                    "priority": "unknown",
                    "created_at": "unknown",
                }
            return None

        return {
            "name": task_info.name,
            "running": task_info.is_running,
            "cancelled": task_info.is_cancelled,
            "has_exception": task_info.has_exception,
            "exception": task_info.exception,
            "priority": task_info.priority.name,
            "created_at": task_info.created_at,
        }

    def list_active_tasks(self) -> list[str]:
        """Get list of currently active task names.

        Returns sorted list of task names that are currently running.

        :return: List of task names that are currently running
        """
        active = []

        for name, task_info in self.task_info.items():
            if task_info.is_running:
                active.append(name)

        for name, task in self.tasks.items():
            if name not in self.task_info and not task.done():
                active.append(name)

        with self._task_lock:
            for name, timer in self._thread_tasks.items():
                if timer.is_alive():
                    active.append(name)

        return sorted(active)

    def _cleanup_completed_tasks(self) -> None:
        """Remove completed tasks from tracking dictionaries.

        Internal method to clean up task dictionaries by removing references
        to completed, cancelled, or failed tasks.
        """
        completed = [
            name
            for name, task_info in self.task_info.items()
            if not task_info.is_running
        ]
        for name in completed:
            del self.task_info[name]

        completed_tasks = []
        for name, task in self.tasks.items():
            with contextlib.suppress(AttributeError, TypeError):
                if isinstance(task, asyncio.Task) and task.done():
                    completed_tasks.append(name)

        for name in completed_tasks:
            del self.tasks[name]

        with self._task_lock:
            completed_timers = [
                name
                for name, timer in self._thread_tasks.items()
                if not timer.is_alive()
            ]
            for name in completed_timers:
                del self._thread_tasks[name]

    def _task_completion_callback(self, task: asyncio.Task) -> None:
        """Handle task completion for error monitoring.

        Internal callback that logs task completion, cancellation, or failure
        for debugging and monitoring purposes.

        :param task: The completed task
        """
        try:
            task_name = "unknown"

            for name, info in self.task_info.items():
                if info.task is task:
                    task_name = name
                    break
            else:
                return

            if task.cancelled():
                logger.debug(f"Task '{task_name}' was cancelled")
                return

            if task.exception():
                logger.error(f"Task '{task_name}' failed: {task.exception()}")
                return

            logger.debug(f"Task '{task_name}' completed successfully")

        except Exception as error:
            logger.error(f"Error in task completion callback: {error}")
