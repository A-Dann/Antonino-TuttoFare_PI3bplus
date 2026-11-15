import logging
import os
import pty
import sys
import termios
import threading
import time

import pytest

from core.input_actions import InputActions
from hal.input.terminal_input import TerminalInput

# --- helper functions ------------------------------------------------------


class NotATerminal:
    def isatty(self):
        return False


@pytest.fixture
def terminal(monkeypatch):
    master, slave = pty.openpty()
    slave_file = os.fdopen(slave, "rb+", buffering=0)
    monkeypatch.setattr(sys, "stdin", slave_file)
    yield master, slave
    slave_file.close()
    os.close(master)


def emit(event):
    pass


@pytest.fixture
def driver(terminal):
    """A TerminalInput that is always stopped at the end of the test, even if the test fails."""
    terminal_driver = TerminalInput()
    yield terminal_driver
    terminal_driver.stop()


def collect_events(expected):
    """Return (collect, events, done): `done` is set once `expected` events have been collected."""
    events = []
    done = threading.Event()

    def collect(event):
        events.append(event)
        if len(events) >= expected:
            done.set()

    return collect, events, done


# --- start -----------------------------------------------------------------


def test_start_twice_creates_only_one_thread(terminal, caplog):
    terminal_driver = TerminalInput()

    terminal_driver.start(emit)
    first_thread = terminal_driver._thread

    with caplog.at_level(logging.DEBUG):
        terminal_driver.start(emit)

    assert first_thread.is_alive()
    assert terminal_driver._thread is first_thread
    assert "already running" in caplog.text

    terminal_driver.stop()


def test_start_without_a_terminal_creates_no_thread(monkeypatch, caplog):
    monkeypatch.setattr(sys, "stdin", NotATerminal())
    driver = TerminalInput()

    with caplog.at_level(logging.WARNING):
        driver.start(emit)

    assert driver._thread is None
    assert "not a terminal" in caplog.text


def test_start_changes_to_cbreak_mode(terminal):
    _, slave = terminal
    terminal_driver = TerminalInput()
    terminal_driver.start(emit)

    flags = termios.tcgetattr(slave)[3]
    assert not flags & termios.ECHO
    assert not flags & termios.ICANON

    terminal_driver.stop()


def test_start_twice_then_stop_restores_the_terminal(terminal):
    _, slave = terminal
    original = termios.tcgetattr(slave)

    terminal_driver = TerminalInput()

    terminal_driver.start(emit)
    terminal_driver.start(emit)
    terminal_driver.stop()

    assert termios.tcgetattr(slave) == original


# --- read loop -------------------------------------------------------------


def test_read_loop_emits_the_action_of_a_key_pressed(terminal, driver):
    master, _ = terminal
    collect, events, done = collect_events(1)
    driver.start(collect)

    os.write(master, b"\x1b[B")

    assert done.wait(timeout=2)
    assert events[0].action == InputActions.DOWN


def test_read_loop_uses_terminal_as_the_source(terminal, driver):
    master, _ = terminal
    collect, events, done = collect_events(1)
    driver.start(collect)

    os.write(master, b"\n")

    assert done.wait(timeout=2)
    assert events[0].source == "Terminal"


def test_read_loop_emits_several_keys_in_order(terminal, driver):
    master, _ = terminal
    collect, events, done = collect_events(3)
    driver.start(collect)

    os.write(master, b"\x1b[B\x1b[B\n")

    assert done.wait(timeout=2)
    assert [event.action for event in events] == [InputActions.DOWN, InputActions.DOWN, InputActions.SELECT]


def test_read_loop_emits_nothing_for_an_unknown_key(terminal, driver):
    master, _ = terminal
    collect, events, done = collect_events(1)
    driver.start(collect)

    os.write(master, b"\x1b[3~")  # Delete: no action
    os.write(master, b"\x1b[A")  # a known key, written after, tells us the loop has gone past Delete

    assert done.wait(timeout=2)
    assert [event.action for event in events] == [InputActions.UP]


def test_read_loop_turns_a_lone_escape_into_back(terminal, driver):
    master, _ = terminal
    collect, events, done = collect_events(1)
    driver.start(collect)

    os.write(master, b"\x1b")

    assert done.wait(timeout=2)
    assert events[0].action == InputActions.BACK


def test_read_loop_joins_a_sequence_split_between_two_reads(terminal, driver):
    master, _ = terminal
    collect, events, done = collect_events(2)
    driver.start(collect)

    os.write(master, b"\x1b[")
    time.sleep(0.03)  # shorter than ESC_TIMEOUT: the first half is read before the second arrives
    os.write(master, b"A")
    os.write(master, b"\n")  # a known key, written after, shows that no stray BACK came before

    assert done.wait(timeout=2)
    assert [event.action for event in events] == [InputActions.UP, InputActions.SELECT]


# --- parse_bytes: keys that are translated ---------------------------------


@pytest.mark.parametrize(
    "data, expected",
    [
        (b"\x1b[A", InputActions.UP),
        (b"\x1b[B", InputActions.DOWN),
        (b"\x1b[C", InputActions.RIGHT),
        (b"\x1b[D", InputActions.LEFT),
        (b"\x1bOA", InputActions.UP),  # arrows in application mode
        (b"\x1bOB", InputActions.DOWN),
        (b"\x1bOC", InputActions.RIGHT),
        (b"\x1bOD", InputActions.LEFT),
        (b"\r", InputActions.SELECT),
        (b"\n", InputActions.SELECT),
        (b"\x7f", InputActions.BACK),
    ],
)
def test_parse_bytes_translates_a_key_into_its_action(data, expected):
    actions, rest = TerminalInput.parse_bytes(data)

    assert actions == [expected]
    assert rest == b""


def test_parse_bytes_keeps_the_order_of_keys_pressed_together():
    actions, rest = TerminalInput.parse_bytes(b"\x1b[B\x1b[B\n\x1b[A")

    assert actions == [InputActions.DOWN, InputActions.DOWN, InputActions.SELECT, InputActions.UP]
    assert rest == b""


def test_parse_bytes_translates_an_arrow_after_a_stray_escape():
    actions, rest = TerminalInput.parse_bytes(b"\x1b\x1b[A")

    assert actions == [InputActions.UP]
    assert rest == b""


# --- parse_bytes: keys that are ignored ------------------------------------


@pytest.mark.parametrize(
    "data",
    [
        b"\x1b[H",  # Home
        b"\x1b[3~",  # Delete
        b"\x1b[15~",  # F5
        b"\x1b[1;5A",  # Ctrl+Up
        b"\x1bx",  # Alt+x
        b"abc",  # letters
        b"",
    ],
)
def test_parse_bytes_ignores_keys_it_does_not_know(data):
    actions, rest = TerminalInput.parse_bytes(data)

    assert actions == []
    assert rest == b""


def test_parse_bytes_ignores_an_unknown_key_between_known_ones():
    actions, rest = TerminalInput.parse_bytes(b"\x1b[B\x1b[3~\x1b[B")

    assert actions == [InputActions.DOWN, InputActions.DOWN]
    assert rest == b""


# --- parse_bytes: incomplete sequences -------------------------------------


@pytest.mark.parametrize(
    "data",
    [
        b"\x1b",
        b"\x1b[",
        b"\x1bO",
        b"\x1b[1;",
    ],
)
def test_parse_bytes_returns_an_incomplete_sequence_as_the_rest(data):
    actions, rest = TerminalInput.parse_bytes(data)

    assert actions == []
    assert rest == data


def test_parse_bytes_translates_what_comes_before_an_incomplete_sequence():
    actions, rest = TerminalInput.parse_bytes(b"\x1b[B\x1b")

    assert actions == [InputActions.DOWN]
    assert rest == b"\x1b"


def test_parse_bytes_completes_a_sequence_split_between_two_reads():
    _, rest = TerminalInput.parse_bytes(b"\x1b[")

    actions, new_rest = TerminalInput.parse_bytes(rest + b"A")

    assert actions == [InputActions.UP]
    assert new_rest == b""


# --- stop ------------------------------------------------------------------


def test_stop_before_start_does_not_raise_errors():
    terminal_driver = TerminalInput()

    terminal_driver.stop()


def test_stop_twice_does_not_raise_errors(terminal):
    terminal_driver = TerminalInput()

    terminal_driver.start(emit)
    terminal_driver.stop()
    terminal_driver.stop()


def test_stop_ends_the_thread(terminal):
    terminal_driver = TerminalInput()

    terminal_driver.start(emit)
    terminal_driver.stop()

    assert not terminal_driver._thread.is_alive()


def test_stop_restores_the_terminal(terminal):
    _, slave = terminal
    original = termios.tcgetattr(slave)

    terminal_driver = TerminalInput()

    terminal_driver.start(emit)
    terminal_driver.stop()

    assert termios.tcgetattr(slave) == original
