import logging
from collections.abc import Callable

import evdev

from core.input_event import InputEvent
from hal.evdev_input import EvdevInput

log = logging.getLogger(__name__)


class InputManager:
    def __init__(self, emit: Callable[[InputEvent], None], driver_classes: list[type[EvdevInput]]) -> None:
        self._emit = emit
        self._driver_classes = driver_classes
        self._drivers: dict[str, EvdevInput] = {}   # path -> running driver
        self._ignored: set[str] = set()             # paths opened and discarded: nobody supports them

    @property
    def drivers(self) -> dict[str, EvdevInput]:
        return dict(self._drivers)

    def start(self) -> None:
        pass

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
        except Exception as e:
            log.exception("Failed to start driver for %s: %s", path, e)
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
        pass
