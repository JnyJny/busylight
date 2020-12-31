"""
"""

import pytest

from time import sleep

from busylight.lights.thread import CancellableThread


def test_cancellable_thread():
    def thread_main():

        while True:
            sleep(0.2)
            yield

    thrd = CancellableThread(thread_main(), "pytest-cancellablethread")

    with pytest.raises(RuntimeError):
        thrd.join()

    thrd.start()

    assert thrd.is_alive()

    thrd.cancel(join=True)

    assert not thrd.is_alive()
