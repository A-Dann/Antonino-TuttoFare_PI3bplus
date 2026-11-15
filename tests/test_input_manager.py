from __future__ import annotations

import threading
import time

import evdev

from hal.input.input_manager import InputManager

EVENT3 = "/dev/input/event3"
EVENT4 = "/dev/input/event4"

# --- fakes -------------------------------------------------------------------


class FakeDevice:
    """Stands for an opened evdev device: remembers its path and whether it was closed."""

    def __init__(self, path):
        self.path = path
        self.closed = False

    def close(self):
        self.closed = True


class FakeDriverSupport:
    """A driver that accepts every device. Records how the manager used it."""

    def __init__(self, device):
        self.device = device
        self.emit = None
        self.started = False
        self.stopped = False

    def start(self, emit):
        self.started = True
        self.emit = emit

    @classmethod
    def supports(cls, device):
        return True

    def stop(self):
        self.stopped = True


class FakeDriverNotSupport(FakeDriverSupport):
    """A driver that refuses every device."""

    @classmethod
    def supports(cls, device):
        return False


class FirstDriver(FakeDriverSupport):
    """Empty subclasses: only there to tell two accepting drivers apart."""


class SecondDriver(FakeDriverSupport):
    pass


class FailingStartDriver(FakeDriverSupport):
    instances: list[FailingStartDriver] = []

    def __init__(self, device):
        super().__init__(device)
        FailingStartDriver.instances.append(self)

    def start(self, emit):
        raise RuntimeError("cannot start")


def emit(event):
    pass


# --- helpers -----------------------------------------------------------------


def make_list_devices(paths):
    """Return (list_devices, paths). Change `paths` between scans to plug / unplug devices."""
    paths = list(paths)

    def list_devices():
        return list(paths)  # a new list on every call, like the real evdev.list_devices

    return list_devices, paths


def make_open_device():
    """Return (open_device, opened_devices). opened_devices lists every device the manager opened."""
    opened_devices = []

    def open_device(path):
        device = FakeDevice(path)
        opened_devices.append(device)
        return device

    return open_device, opened_devices


def build_manager(monkeypatch, paths, driver_classes, scan_interval=0.01):
    """Replace the two evdev functions with fakes and build a manager.

    Return (manager, paths, opened_devices): the test changes `paths` to plug or
    unplug devices, and reads `opened_devices` to see what the manager opened.
    The scan interval is tiny by default so the tests that start the thread are fast.
    """
    list_devices, paths = make_list_devices(paths)
    open_device, opened_devices = make_open_device()
    monkeypatch.setattr(evdev, "list_devices", list_devices)
    monkeypatch.setattr(evdev, "InputDevice", open_device)

    return InputManager(emit, driver_classes, scan_interval), paths, opened_devices


def count_scans(monkeypatch, manager, expected, failing=False):
    """Wrap manager.scan and return (done, calls).

    `done` is set once `expected` scans have finished (the real scan has already
    run when it is set), so a test waits on it instead of guessing a sleep.
    With failing=True every scan raises instead of running.
    """
    done = threading.Event()
    calls = []
    real_scan = manager.scan

    def scan():
        calls.append(1)
        try:
            if failing:
                raise RuntimeError("boom")
            real_scan()
        finally:
            if len(calls) >= expected:
                done.set()

    monkeypatch.setattr(manager, "scan", scan)
    return done, calls


# --- stop --------------------------------------------------------------------

def test_stop_before_start_does_not_fail(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [], [])

    manager.stop()


def test_stop_can_be_called_twice(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [EVENT3], [FakeDriverSupport])
    manager.scan()

    manager.stop()
    manager.stop()

    assert manager.drivers == {}


def test_stop_stops_every_active_driver(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [EVENT3, EVENT4], [FakeDriverSupport])
    manager.scan()
    drivers = list(manager.drivers.values())

    manager.stop()

    assert len(drivers) == 2
    assert all(driver.stopped for driver in drivers)
    assert manager.drivers == {}


def test_stop_forgets_the_ignored_devices(monkeypatch):
    manager, _, opened_devices = build_manager(monkeypatch, [EVENT3], [FakeDriverNotSupport])
    manager.scan()

    manager.stop()
    manager.scan()

    assert len(opened_devices) == 2


# --- the scan thread ---------------------------------------------------------

def test_start_scans_repeatedly_in_the_background(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [], [FakeDriverSupport])
    done, calls = count_scans(monkeypatch, manager, 3)

    manager.start()
    assert done.wait(timeout=2)
    manager.stop()

    assert len(calls) >= 3


def test_start_finds_a_device_without_anyone_calling_scan(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [EVENT3], [FakeDriverSupport])
    done, _ = count_scans(monkeypatch, manager, 1)

    manager.start()
    assert done.wait(timeout=2)
    found = set(manager.drivers)
    manager.stop()

    assert found == {EVENT3}


def test_start_twice_creates_one_thread(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [], [FakeDriverSupport])

    manager.start()
    first_thread = manager._thread
    manager.start()
    second_thread = manager._thread
    manager.stop()

    assert second_thread is first_thread


def test_stop_ends_the_thread(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [], [FakeDriverSupport])
    manager.start()
    thread = manager._thread

    manager.stop()

    assert thread is not None
    assert not thread.is_alive()


def test_stop_does_not_wait_for_the_scan_interval(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [], [FakeDriverSupport], scan_interval=30)
    done, _ = count_scans(monkeypatch, manager, 1)
    manager.start()
    assert done.wait(timeout=2)  # the thread is now waiting for the next scan

    started = time.perf_counter()
    manager.stop()
    elapsed = time.perf_counter() - started

    assert elapsed < 1


def test_scan_loop_survives_a_failing_scan(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [], [FakeDriverSupport])
    done, calls = count_scans(monkeypatch, manager, 3, failing=True)

    manager.start()
    assert done.wait(timeout=2)
    manager.stop()

    assert len(calls) >= 3


def test_scan_loop_still_waits_between_failing_scans(monkeypatch):
    interval = 0.05
    manager, _, _ = build_manager(monkeypatch, [], [FakeDriverSupport], scan_interval=interval)
    done, _ = count_scans(monkeypatch, manager, 3, failing=True)

    started = time.perf_counter()
    manager.start()
    assert done.wait(timeout=2)
    elapsed = time.perf_counter() - started
    manager.stop()

    # 3 scans mean at least 2 waits: without them the loop would spin at full speed
    assert elapsed >= 2 * interval * 0.8


# --- a device that cannot be opened ------------------------------------------


def test_scan_skips_a_device_that_cannot_be_opened(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [EVENT3], [FakeDriverSupport])

    def failing_open(path):
        raise PermissionError("denied")

    monkeypatch.setattr(evdev, "InputDevice", failing_open)

    manager.scan()

    assert manager.drivers == {}


def test_scan_does_not_retry_a_device_that_cannot_be_opened(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [EVENT3], [FakeDriverSupport])
    attempts = []

    def failing_open(path):
        attempts.append(path)
        raise PermissionError("denied")

    monkeypatch.setattr(evdev, "InputDevice", failing_open)

    manager.scan()
    manager.scan()

    assert attempts == [EVENT3]


# --- a driver that fails to start --------------------------------------------


def test_scan_stops_a_driver_that_fails_to_start_and_does_not_register_it(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [EVENT3], [FailingStartDriver])

    manager.scan()

    assert FailingStartDriver.instances[-1].stopped
    assert manager.drivers == {}


# --- a supported device ------------------------------------------------------


def test_scan_creates_a_driver_for_a_new_supported_device(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [EVENT3], [FakeDriverSupport])

    manager.scan()

    assert manager.drivers[EVENT3].device.path == EVENT3


def test_scan_starts_the_new_driver_with_the_emit_function(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [EVENT3], [FakeDriverSupport])

    manager.scan()

    driver = manager.drivers[EVENT3]
    assert driver.started
    assert driver.emit is emit


def test_scan_creates_a_driver_for_each_new_device(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [EVENT3, EVENT4], [FakeDriverSupport])

    manager.scan()

    assert set(manager.drivers) == {EVENT3, EVENT4}


def test_scan_does_not_create_a_second_driver_for_a_known_device(monkeypatch):
    manager, _, opened_devices = build_manager(monkeypatch, [EVENT3], [FakeDriverSupport])
    manager.scan()
    first_driver = manager.drivers[EVENT3]

    manager.scan()

    assert len(opened_devices) == 1
    assert manager.drivers[EVENT3] is first_driver


# --- an unsupported device ---------------------------------------------------


def test_scan_closes_an_unsupported_device_and_creates_no_driver(monkeypatch):
    manager, _, opened_devices = build_manager(monkeypatch, [EVENT3], [FakeDriverNotSupport])

    manager.scan()

    assert opened_devices[0].closed
    assert manager.drivers == {}


def test_scan_does_not_reopen_an_unsupported_device(monkeypatch):
    manager, _, opened_devices = build_manager(monkeypatch, [EVENT3], [FakeDriverNotSupport])

    manager.scan()
    manager.scan()

    assert len(opened_devices) == 1


# --- a device that disappears ------------------------------------------------


def test_scan_stops_and_removes_the_driver_of_a_device_that_disappeared(monkeypatch):
    manager, paths, _ = build_manager(monkeypatch, [EVENT3], [FakeDriverSupport])
    manager.scan()
    driver = manager.drivers[EVENT3]

    paths.clear()
    manager.scan()

    assert driver.stopped
    assert manager.drivers == {}


def test_scan_forgets_an_unsupported_device_that_disappeared(monkeypatch):
    manager, paths, opened_devices = build_manager(monkeypatch, [EVENT3], [FakeDriverNotSupport])
    manager.scan()

    paths.clear()
    manager.scan()
    paths.append(EVENT3)  # something is plugged in again on the same path
    manager.scan()

    assert len(opened_devices) == 2


# --- which driver class is chosen --------------------------------------------


def test_scan_assigns_the_first_driver_class_that_supports_the_device(monkeypatch):
    manager, _, _ = build_manager(monkeypatch, [EVENT3], [FakeDriverNotSupport, FirstDriver, SecondDriver])

    manager.scan()

    assert type(manager.drivers[EVENT3]) is FirstDriver
