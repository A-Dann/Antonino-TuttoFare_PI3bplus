import logging

from core.context import AppContext
from core.event_bus import EventBus
from core.interfaces.plugin_interface import Plugin
from core.plugin_manager import PluginManager
from core.state_keys import StateKeys
from core.state_manager import StateManager
from ui.navigation import Navigator


# --- helpers ---------------------------------------------------------------

class RecordingPlugin(Plugin):
    """Plugin that appends ("start"/"stop", name) to a shared list."""

    def __init__(self, name, calls, fail_on_start=False, fail_on_stop=False):
        self.name = name
        self.calls = calls
        self.fail_on_start = fail_on_start
        self.fail_on_stop = fail_on_stop
        self.received_ctx = None

    def start(self, ctx):
        self.received_ctx = ctx
        if self.fail_on_start:
            raise RuntimeError("start boom")
        self.calls.append(("start", self.name))

    def stop(self):
        if self.fail_on_stop:
            raise RuntimeError("stop boom")
        self.calls.append(("stop", self.name))


def make_manager(*plugins):
    """A PluginManager that already holds the given plugins (no discovery)."""
    ctx = object()
    manager = PluginManager(ctx)
    for plugin in plugins:
        manager._plugins[plugin.name] = plugin
    return manager, ctx


# --- discover --------------------------------------------------------------

def test_discover_finds_the_menu_plugin_and_start_all_activates_main_screen():
    event_bus = EventBus()
    state_manager = StateManager(event_bus)
    ctx = AppContext(event_bus, state_manager, Navigator(state_manager))
    manager = PluginManager(ctx)

    manager.discover()
    manager.start_all()

    assert state_manager.get(StateKeys.ACTIVE_SCREEN) == "Main"


# --- start_all -------------------------------------------------------------

def test_start_all_starts_every_plugin_and_passes_the_context():
    calls = []
    first = RecordingPlugin("first", calls)
    second = RecordingPlugin("second", calls)
    manager, ctx = make_manager(first, second)

    manager.start_all()

    assert calls == [("start", "first"), ("start", "second")]
    assert first.received_ctx is ctx
    assert second.received_ctx is ctx


def test_start_all_logs_error_when_a_plugin_fails(caplog):
    calls = []
    manager, _ = make_manager(RecordingPlugin("broken", calls, fail_on_start=True))

    with caplog.at_level(logging.ERROR):
        manager.start_all()

    assert "Error starting plugin broken" in caplog.text


def test_start_all_keeps_starting_after_a_plugin_fails():
    calls = []
    manager, _ = make_manager(
        RecordingPlugin("broken", calls, fail_on_start=True),
        RecordingPlugin("healthy", calls),
    )

    manager.start_all()

    assert calls == [("start", "healthy")]


# --- stop_all --------------------------------------------------------------

def test_stop_all_stops_plugins_in_reverse_start_order():
    calls = []
    manager, _ = make_manager(
        RecordingPlugin("first", calls),
        RecordingPlugin("second", calls),
        RecordingPlugin("third", calls),
    )
    manager.start_all()
    calls.clear()

    manager.stop_all()

    assert calls == [("stop", "third"), ("stop", "second"), ("stop", "first")]


def test_stop_all_does_not_stop_plugins_that_failed_to_start():
    calls = []
    manager, _ = make_manager(
        RecordingPlugin("broken", calls, fail_on_start=True),
        RecordingPlugin("healthy", calls),
    )
    manager.start_all()
    calls.clear()

    manager.stop_all()

    assert calls == [("stop", "healthy")]


def test_stop_all_logs_error_and_keeps_stopping_the_others(caplog):
    calls = []
    manager, _ = make_manager(
        RecordingPlugin("first", calls),
        RecordingPlugin("broken", calls, fail_on_stop=True),
    )
    manager.start_all()
    calls.clear()

    with caplog.at_level(logging.ERROR):
        manager.stop_all()

    assert "Error stopping plugin broken" in caplog.text
    assert calls == [("stop", "first")]


def test_stop_all_called_twice_stops_each_plugin_once():
    calls = []
    manager, _ = make_manager(RecordingPlugin("only", calls))
    manager.start_all()
    calls.clear()

    manager.stop_all()
    manager.stop_all()

    assert calls == [("stop", "only")]