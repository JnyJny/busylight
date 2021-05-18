"""A threading.Thread subclass that can be cancelled.

"""

from time import sleep
from threading import Thread
from typing import Generator

from loguru import logger


class CancellableThread(Thread):
    """A threading.Thread that can be cancelled

    A CancellableThread can be stopped asynchronously by the main thread
    if the supplied generator cooperates. The function executed in the
    `run` method must call `yield` periodically. The thread will be more
    responsive to cancelling if generator yields often. A thread should
    not be re-used after it has been cancelled.

    The generator function should yeild a floating point value, indicating
    the time in seconds to wait before the next iteration of the generator.


    """

    def __init__(self, target: Generator[float, None, None], name: str = None) -> None:
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

    @property
    def alive(self) -> bool:
        return self.is_alive()

    @property
    def cancelled(self) -> bool:
        return getattr(self, "_cancelled", False)

    @cancelled.setter
    def cancelled(self, value: bool) -> None:
        self._cancelled = value

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
        logger.debug(f" {self} running target {self._target}")
        while not self.cancelled:
            try:
                result = next(self._target)
                logger.debug(f"target result {result}")
                sleep(result)
            except Exception as error:
                logger.error(f"{error}")
                break

        logger.debug(f"{self} returning")

    def cancel(self) -> None:
        """Signals that the thread should terminate as soon as possible.

        Call this method from the main thread on the running thread.
        """
        self.cancelled = True
