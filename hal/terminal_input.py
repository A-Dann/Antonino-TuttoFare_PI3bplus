from __future__ import annotations

import logging
import os
import select
import sys
import termios
import threading
import tty
from collections.abc import Callable
from typing import Any

from core.input_actions import InputActions
from core.input_event import InputEvent
from hal.input_interface import InputInterface

log = logging.getLogger(__name__)

ESC = 0x1B
CSI_INTRODUCER = ord("[")
SS3_INTRODUCER = ord("O")

# Time to wait for the rest of an escape sequence before a lone ESC is taken as the Esc key.
ESC_TIMEOUT = 0.1
READ_TIMEOUT = 0.5
JOIN_TIMEOUT = 1.0

# Single-byte keys.
KEYS: dict[bytes, InputActions] = {
    b"\r": InputActions.SELECT,
    b"\n": InputActions.SELECT,
    b"\x7f": InputActions.BACK,
}

# Complete escape sequences. Arrows are sent as ESC [ x, or as ESC O x in application mode.
SEQUENCES: dict[bytes, InputActions] = {
    b"\x1b[A": InputActions.UP,
    b"\x1b[B": InputActions.DOWN,
    b"\x1b[C": InputActions.RIGHT,
    b"\x1b[D": InputActions.LEFT,
    b"\x1bOA": InputActions.UP,
    b"\x1bOB": InputActions.DOWN,
    b"\x1bOC": InputActions.RIGHT,
    b"\x1bOD": InputActions.LEFT,
}

class TerminalInput(InputInterface):
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._stop_signal = threading.Event()
        self._fd: int | None = None
        self._saved_settings: list[Any] | None = None

    @property
    def name(self) -> str:
        return "Terminal"

    def start(self, emit: Callable[[InputEvent], None]) -> None:
        if self._thread is not None and self._thread.is_alive():
            log.debug("TerminalInput is already running")
            return

        if not sys.stdin.isatty():
            log.warning("Standard input is not a terminal; TerminalInput disabled.")
            return

        fd = sys.stdin.fileno()
        self._fd = fd
        self._saved_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

        self._stop_signal.clear()
        self._thread = threading.Thread(target=self.read_loop, args=(emit, fd), daemon=True)
        self._thread.start()

    def read_loop(self, emit: Callable[[InputEvent], None], fd: int) -> None:
        pending = b""
        while not self._stop_signal.is_set():
            try:
                timeout = ESC_TIMEOUT if pending else READ_TIMEOUT
                readable, _, _ = select.select([fd], [], [], timeout)

                if not readable:
                    if pending == bytes([ESC]):
                        self._emit_action(InputActions.BACK, emit)
                    pending = b""
                    continue

                data = os.read(fd, 1024)
                if not data:
                    log.warning("Terminal closed, TerminalInput stops reading.")
                    break

                actions, pending = self.parse_bytes(pending + data)
                for action in actions:
                    self._emit_action(action, emit)
            except OSError:
                if self._stop_signal.is_set():
                    log.exception("Error during TerminalInput read loop")
                break

    def _emit_action(self, action: InputActions, emit: Callable[[InputEvent], None]) -> None:
        emit(InputEvent(action, self.name))

    @staticmethod
    def parse_bytes(data: bytes) -> tuple[list[InputActions], bytes]:
        """Translate raw terminal bytes into actions.

        Return the actions found and the trailing bytes that may be the start of an
        escape sequence: the caller keeps them and prepends them to the next read.
        Sequences that are not in SEQUENCES (Home, Delete, F-keys...) are ignored.
        """
        actions: list[InputActions] = []
        i = 0
        n = len(data)

        while i < n:
            if data[i] != ESC:
                action = KEYS.get(data[i : i + 1])
                if action is not None:
                    actions.append(action)
                i += 1
                continue

            if i + 1 >= n:
                return actions, data[i:]

            introducer = data[i + 1]
            if introducer == CSI_INTRODUCER:
                end = i + 2
                while end < n and 0x20 <= data[end] <= 0x3F:  # parameter and intermediate bytes
                    end += 1
                if end >= n:
                    return actions, data[i:]
                end += 1  # the final byte
            elif introducer == SS3_INTRODUCER:
                end = i + 3
                if end > n:
                    return actions, data[i:]
            else:
                i += 1  # ESC followed by another key (for example Alt+key): ignore the ESC
                continue

            action = SEQUENCES.get(data[i:end])
            if action is not None:
                actions.append(action)
            i = end

        return actions, b""

    def stop(self) -> None:
        self._stop_signal.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=JOIN_TIMEOUT)

        self._restore_terminal()

    def _restore_terminal(self) -> None:
        if self._fd is None or self._saved_settings is None:
            return

        try:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved_settings)
        except (termios.error, OSError):
            log.exception("Failed to restore terminal settings")
        finally:
            self._saved_settings = None
