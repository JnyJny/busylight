"""
"""

import asyncio

from typing import Awaitable, Optional


class Taskable:
    @property
    def event_loop(self):
        """"""
        try:
            return self._event_loop
        except AttributeError:
            pass
        self._event_loop = asyncio.get_event_loop()
        return self._event_loop

    @property
    def tasks(self) -> dict[str, asyncio.Task]:
        """"""
        try:
            return self._tasks
        except AttributeError:
            pass
        self._tasks = {}
        return self._tasks

    def add_task(self, name: str, coroutine: Awaitable) -> asyncio.Task:
        """"""
        try:
            task = self.tasks[name]
            return task
        except KeyError:
            pass

        name += f"-{id(self)}"

        self.tasks[name] = self.event_loop.create_task(coroutine(self), name=name)

        return self.tasks[name]

    def cancel_task(self, name: str) -> Optional[asyncio.Task]:
        """"""
        try:
            task = self.tasks[name]
            del self.tasks[name]
            task.cancel()
            return task
        except (KeyError, AttributeError) as error:
            pass

        return None

    def cancel_tasks(self) -> None:
        """"""
        for task in self.tasks.values():
            task.cancel()
        self.tasks.clear()