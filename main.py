import time
from core.event_bus import event_bus
from core.state_manager import state_manager
from core.plugin_manager import PluginManager
from plugins.menu_components.cli_menu_renderer import render_menu

def main():
    print("Starting system...")
    
    # Inizializzazione del plugin manager
    plugin_manager = PluginManager(event_bus, state_manager)
    
    # Imposta lo stato iniziale del menu attivo
    state_manager.set("active_menu", "Main Menu")
    
    print("System started successfully.\n")
    
    try:
        # Avvia il renderer CLI del menu
        render_menu(event_bus, state_manager)
            
    except KeyboardInterrupt:
        print("\nShutting down system...")
        print("System stopped cleanly.")

if __name__ == "__main__":
    main()