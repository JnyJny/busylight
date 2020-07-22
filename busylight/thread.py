"""A thread for controlling USBLight effects.
"""

from threading import Thread
from typing import Generator


class EffectThread(Thread):
    def __init__(self, target: Generator, name: str = None):
        """
        """
        super().__init__(target=target, name=name, daemon=True)
        self._is_cancelled = False

    def run(self) -> None:
        """Executes the `target` generator until the thread is cancelled.

        The `target` is expected to perform a long running operation
        that periodically calls yield to allow the EffectThread to
        check if it's been cancelled. 

        :param target: Generator that yields

        ```python
        def long_running(interval:int = 1) -> None:
            while True:
                  # some operation here
                  yield
                  time.sleep(interval)
        ```
        
        """
        while True:
            for _ in self._target():
                if self._is_cancelled:
                    return

    def cancel(self) -> None:
        """Stops the thread provided the `target` callable is yielding
        control to the `EffectThread.run` method at a reasonable rate.
        The sooner the target yields, the quicker the thread will
        cancel. Once a thread is cancelled, the caller will need to
        call `join` to clean up the thread. 
        """
        self._is_cancelled = True
