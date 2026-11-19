import os
import select
import threading

import pytest

from hal.input.wakeup import WakeUp


def is_readable(wakeup):
    readable, _, _ = select.select([wakeup.fileno()], [], [], 0)
    return bool(readable)


@pytest.fixture
def wakeup():
    """A WakeUp that is always closed at the end of the test."""
    instance = WakeUp()
    yield instance
    instance.close()


# --- set ---------------------------------------------------------------------

def test_a_new_wakeup_is_not_readable(wakeup):
    assert not is_readable(wakeup)


def test_set_makes_the_wakeup_readable(wakeup):
    wakeup.set()

    assert is_readable(wakeup)


def test_set_many_times_never_blocks(wakeup):
    # more bytes than a pipe can hold: a blocking write would hang here (pytest-timeout stops it)
    for _ in range(100_000):
        wakeup.set()

    assert is_readable(wakeup)


def test_set_wakes_a_thread_blocked_in_select(wakeup):
    thread = threading.Thread(target=lambda: select.select([wakeup.fileno()], [], []), daemon=True)
    thread.start()

    wakeup.set()
    thread.join(timeout=2)

    assert not thread.is_alive()


# --- close -------------------------------------------------------------------

def test_set_after_close_does_nothing():
    wakeup = WakeUp()
    wakeup.close()

    wakeup.set()


def test_close_can_be_called_twice():
    wakeup = WakeUp()

    wakeup.close()
    wakeup.close()


@pytest.mark.skipif(not os.path.isdir("/proc/self/fd"), reason="needs /proc")
def test_close_releases_the_file_descriptors():
    before = len(os.listdir("/proc/self/fd"))
    wakeup = WakeUp()

    wakeup.close()

    assert len(os.listdir("/proc/self/fd")) == before
