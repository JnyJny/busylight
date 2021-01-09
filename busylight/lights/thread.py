"""A threading.Thread subclass that can be cancelled.

"""

from threading import Thread
from typing import Generator


class CancellableThread(Thread):
    """A threading.Thread that can be cancelled

    A CancellableThread can be stopped asynchronously by the main thread
    if the supplied generator cooperates. The function executed in the
    `run` method must call `yield` periodically. The thread will be more
    responsive to cancelling if generator yields often. A thread should
    not be re-used after it has been cancelled.
    """

    def __init__(self, target: Generator[None, None, None], name: str = None):
        """
        :param target: generator
        :param name: str
        """
        if not isinstance(target, Generator):
            raise ValueError(f"Target must be a generator, not: {type(target)}")

        super().__init__(
            target=target,  # type:ignore
            name=name,
            daemon=True,
        )
        self._is_cancelled = False

    def run(self) -> None:
        """Executes the `target` generator until the thread is cancelled.

        The `target` generator is expected to perform a long running operation
        that periodically calls "yield" to allow the thread to check if
        it has been cancelled.

        ```python
        def long_running(interval:float = 1.0) -> None:
            while True:
                  # some operation here
                  yield
                  time.sleep(interval)
        ```

        """
        for _ in self._target:  # type: ignore
            if self._is_cancelled:
                return

    def cancel(self, join: bool = True, timeout: float = 0.05) -> None:
        """Signals that the thread should terminate as soon as possible.

        Call this method from the main thread on the running thread.

        :param join: bool
        :param timeout: float
        """
        self._is_cancelled = True
        if join:
            while self.is_alive():
                self.join(timeout)
