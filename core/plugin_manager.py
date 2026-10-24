import importlib
import os

class PluginManager():
    def __init__(self, event_bus, state_manager):
        self._event_bus = event_bus
        self._state_manager = state_manager
        self._plugins_dir = "plugins"
        self._plugins = {}

        self.load_plugins()
        self.setup_plugins()

    def load_plugins(self):
        # Scan the plugins directory and load python files
        for filename in os.listdir(self._plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__init__"):
                plugin_name = filename[:-3]
                self.add_plugin(plugin_name)
                
    def add_plugin(self, key: str):
        # Dynamically import the plugin module
        module_path = f"plugins.{key}"
        plugin_module = importlib.import_module(module_path)

        # Checks if the plugin implements plugins_interface
        if not hasattr(plugin_module, "init") or not callable(plugin_module.init):
            raise TypeError(f"{key} plugin does not respect the plugin_interface contract.")
        
        self._plugins[key] = plugin_module

    def setup_plugins(self):
        # Initialize loaded plugins by passing core dependencies
        for plugin_module in self._plugins.values():
            if hasattr(plugin_module, "init"):
                plugin_module.init(self._event_bus, self._state_manager)