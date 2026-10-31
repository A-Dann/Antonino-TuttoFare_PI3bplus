# core/plugin_manager.py
from __future__ import annotations
from typing import TYPE_CHECKING
import importlib
import inspect
import logging
from pathlib import Path

import plugins as plugins_pkg
from core.interfaces.plugin_interface import Plugin

if TYPE_CHECKING:
    from core.context import AppContext

log = logging.getLogger(__name__)

PLUGIN_FILE_PATTERN = "*_plugin.py"


class PluginManager:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx
        self._plugins: dict[str, Plugin] = {}
        self._started: list[str] = []

    def discover(self) -> None:
        """Find, import and instantiate every plugin under plugins/."""
        for module_name in self._find_module_names():
            module = self._import_module(module_name)
            if module is None:
                continue
            for cls in self._find_plugin_classes(module):
                self._register(module_name, cls)

    @staticmethod
    def _find_module_names() -> list[str]:
        """plugins/menu/menu_plugin.py -> 'plugins.menu.menu_plugin'"""
        root = Path(next(iter(plugins_pkg.__path__)))
        names = []
        for file in sorted(root.rglob(PLUGIN_FILE_PATTERN)):
            parts = file.relative_to(root).with_suffix("").parts
            names.append(".".join((plugins_pkg.__name__, *parts)))
        return names

    @staticmethod
    def _import_module(module_name: str):
        try:
            return importlib.import_module(module_name)
        except Exception:
            log.exception("Cannot import %s", module_name)
            return None

    @staticmethod
    def _find_plugin_classes(module) -> list[type[Plugin]]:
        """Concrete Plugin subclasses defined in this module (not imported)."""
        classes = [
            cls for _, cls in inspect.getmembers(module, inspect.isclass)
            if issubclass(cls, Plugin)
            and cls.__module__ == module.__name__
            and not inspect.isabstract(cls)
        ]
        if not classes:
            log.warning("%s defines no Plugin subclass", module.__name__)
        return classes

    def _register(self, module_name: str, cls: type[Plugin]) -> None:
        plugin_id = f"{module_name}.{cls.__name__}"
        try:
            self._plugins[plugin_id] = cls()
            log.info("Discovered plugin: %s", plugin_id)
        except Exception:
            log.exception("Cannot instantiate %s", plugin_id)

    def start_all(self):
        """Initialize and start all discovered plugins."""
        for name, module in self._plugins.items():
            try:
                log.info("Starting plugin: %s", name)
                module.start(self._ctx)
                self._started.append(name)
            except Exception:
                log.exception("Error starting plugin %s", name)

    def stop_all(self) -> None:
        for plugin_id in reversed(self._started):
            try:
                self._plugins[plugin_id].stop()
            except Exception:
                log.exception("Error stopping plugin %s", plugin_id)
        self._started.clear()