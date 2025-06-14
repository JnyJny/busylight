"""Asynchronous task support for animating lights."""

import asyncio
from collections.abc import Awaitable
from functools import cached_property
from typing import Dict, Optional


class TaskableMixin:
    """This mixin class is designed to associate and manage
    asynchronous tasks. Tasks can be added and cancelled.
    """

    @cached_property
    def event_loop(self):
        """The default event loop."""
        return asyncio.get_event_loop()

    @cached_property
    def tasks(self) -> Dict[str, asyncio.Task]:
        """Active tasks that are associated with this class."""
        return {}

    def add_task(self, name: str, coroutine: Awaitable) -> asyncio.Task:
        """Create a new task using coroutine as the body and stash it in
        the tasks dictionary property using name as a key.

        :name: str
        :coroutine: Awaitable
        :return: asyncio.Task
        """
        try:
            task = self.tasks[name]
            return task
        except KeyError:
            pass

        # >py3.7, create_task takes a `name` parameter
        self.tasks[name] = self.event_loop.create_task(coroutine(self))

        return self.tasks[name]

    def cancel_task(self, name: str) -> Optional[asyncio.Task]:
        """Cancels a task associated with name if it exists.  If the
        task exists the cancelled task is returned, otherwise None.

        :name: str
        :return: None | asyncio.Task
        """
        try:
            task = self.tasks[name]
            del self.tasks[name]
            task.cancel()
            return task
        except (KeyError, AttributeError):
            pass

        return None

    def cancel_tasks(self) -> None:
        """Cancels all tasks and returns nothing."""
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()
