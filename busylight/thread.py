"""A threading.Thread subclass that can be cancelled.

"""

from threading import Thread
from typing import Generator


class CancellableThread(Thread):
    def __init__(self, target: Generator, name: str = None):
        """
        :param target: generator
        :param name: str
        """
        if not isinstance(target, Generator):
            raise ValueError("Target must be a generator.")

        super().__init__(target=target, name=name, daemon=True)
        self._is_cancelled = False

    def run(self) -> None:
        """Executes the `target` generator until the thread is cancelled.

        The `target` generator is expected to perform a long running operation
        that periodically calls "yield" to allow the thread to check if
        it has been cancelled.

        ```python
        def long_running(interval:int = 1) -> None:
            while True:
                  # some operation here
                  yield
                  time.sleep(interval)
        ```
        
        """
        while True:
            for _ in self._target:
                if self._is_cancelled:
                    return

    def cancel(self, join: bool = True, timeout: float = 0.05) -> None:
        """Signals to the `run` method that the thread should terminate.

        :param join: bool
        :param timeout: float
        """
        self._is_cancelled = True
        if join:
            while self.is_alive():
                self.join(timeout)
