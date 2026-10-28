import importlib
import logging
import pkgutil
import plugins as plugins_pkg

log = logging.getLogger(__name__)

class PluginManager():
    def __init__(self, ctx):
        self._ctx = ctx
        self._plugins = {}

        self.discover()
        self.start_all()

    def discover(self):
        """Discover all available plugins in the plugins/ package."""
        for info in pkgutil.iter_modules(plugins_pkg.__path__):
            module_name = f"{plugins_pkg.__name__}.{info.name}"
            try:
                module = importlib.import_module(module_name)
                
                if not hasattr(module, "init") or not callable(module.init):
                    raise TypeError(f"Plugin '{info.name}' does not define a valid init(ctx) function.")
                
                self._plugins[info.name] = module
                log.info(f"Discovered plugin: {info.name}")
            except Exception as e:
                log.error(f"Error discovering plugin {info.name}: {e}")

    def start_all(self):
        """Initialize and start all discovered plugins."""
        for name, module in self._plugins.items():
            try:
                log.info(f"Starting plugin: {name}")
                module.init(self._ctx)
            except Exception as e:
                log.error(f"Error starting plugin {name}: {e}")