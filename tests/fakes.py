from __future__ import annotations

import os
import threading


class DummyKeyboard:
    """Fake evdev device: a pipe plays the role of /dev/input/eventN.

    send() writes a byte into the pipe, which makes select() report the
    device as ready, exactly as a real key press would.
    """

    name = "dummy_keyboard"

    def __init__(self, events, error=None, first_read_error=None):
        self._read_fd, self._write_fd = os.pipe()
        self.fd = self._read_fd
        self._events = events
        self._error = error
        self._first_read_error = first_read_error
        self.is_closed = False

    def send(self):
        os.write(self._write_fd, b"x")

    def read(self):
        os.read(self._read_fd, 1)  # consume the byte, otherwise select() stays "ready"
        if self._first_read_error is not None:
            error, self._first_read_error = self._first_read_error, None
            raise error
        if self._error is not None:
            raise self._error
        yield from self._events

    def close(self):
        if not self.is_closed:
            os.close(self._read_fd)
            os.close(self._write_fd)
        self.is_closed = True


def collect():
    """Return (emit, events): emit stores every event it receives."""
    events = []

    def emit(event):
        events.append(event)

    return emit, events


def collect_expected(expected):
    """Like collect(), but also return `done`, set when `expected` events have arrived.

    Needed when emit is called from another thread: the test waits on `done`
    instead of guessing how long to sleep.
    """
    events = []
    done = threading.Event()

    def emit(event):
        events.append(event)
        if len(events) >= expected:
            done.set()

    return emit, events, done