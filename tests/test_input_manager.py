from __future__ import annotations

import evdev

from hal.input_manager import InputManager

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
    instances = []

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


def build_manager(monkeypatch, paths, driver_classes):
    """Replace the two evdev functions with fakes and build a manager.

    Return (manager, paths, opened_devices): the test changes `paths` to plug or
    unplug devices, and reads `opened_devices` to see what the manager opened.
    """
    list_devices, paths = make_list_devices(paths)
    open_device, opened_devices = make_open_device()
    monkeypatch.setattr(evdev, "list_devices", list_devices)
    monkeypatch.setattr(evdev, "InputDevice", open_device)

    return InputManager(emit, driver_classes), paths, opened_devices


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
