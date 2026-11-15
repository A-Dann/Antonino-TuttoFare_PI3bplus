import logging
import threading
from collections.abc import Callable

import evdev

from core.input_event import InputEvent
from hal.input.evdev_input import EvdevInput

log = logging.getLogger(__name__)

JOIN_TIMEOUT = 5.0


class InputManager:
    def __init__(
        self,
        emit: Callable[[InputEvent], None],
        driver_classes: list[type[EvdevInput]],
        scan_interval: float = 2.0,
    ) -> None:

        self._thread: threading.Thread | None = None
        self._stop_signal = threading.Event()
        self._scan_interval = scan_interval
        self._emit = emit
        self._driver_classes = driver_classes
        self._drivers: dict[str, EvdevInput] = {}   # path -> running driver
        self._ignored: set[str] = set()             # paths opened and discarded: nobody supports them

    @property
    def drivers(self) -> dict[str, EvdevInput]:
        return dict(self._drivers)

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            log.debug("Thread is already alive")
            return

        self._thread = threading.Thread(target=self._scan_loop, daemon=True)
        self._thread.start()

    def _scan_loop(self) -> None:
        while not self._stop_signal.is_set():
            try:
                self.scan()
            except Exception:
                log.exception("An error has occurred")

            self._stop_signal.wait(self._scan_interval)

    def scan(self) -> None:
        present = set(evdev.list_devices())
        known = set(self._drivers) | self._ignored

        for path in present - known:
            self._add_device(path)

        for path in known - present:
            self._remove_device(path)

    def _add_device(self, path: str) -> None:
        try:
            device = evdev.InputDevice(path)
        except OSError as e:
            log.warning("Failed to open device %s: %s", path, e)
            self._ignored.add(path)
            return

        driver_class = self._find_driver_class(device)

        if driver_class is None:
            log.debug("No matching driver found for device %s, ignoring.", path)
            device.close()
            self._ignored.add(path)
            return

        driver = driver_class(device)
        try:
            driver.start(self._emit)
        except Exception:
            log.exception("Failed to start driver for %s", path)
            driver.stop()
            self._ignored.add(path)
            return

        self._drivers[path] = driver
        log.info("Device successfully started: %s (%s)", path, driver_class.__name__)

    def _remove_device(self, path: str) -> None:
        if path in self._drivers:
            self._drivers.pop(path).stop()
        else:
            self._ignored.discard(path)

    def _find_driver_class(self, device: evdev.InputDevice) -> type[EvdevInput] | None:
        for driver_class in self._driver_classes:
            if driver_class.supports(device):
                return driver_class

        return None

    def stop(self) -> None:
        self._stop_signal.set()
        if self._thread is not None:
            self._thread.join(JOIN_TIMEOUT)
            if self._thread.is_alive():
                log.warning("Thread is still alive after join timed-out")

        paths = list(self._drivers)
        for path in paths:
            self._remove_device(path)
        self._ignored.clear()
