import time
from core.event_bus import event_bus
from core.state_manager import state_manager
from core.plugin_manager import PluginManager

def main():
    print("Starting system...")
    
    # Inizializzazione del plugin manager
    plugin_manager = PluginManager(event_bus, state_manager)
    
    # Imposta lo stato iniziale dello schermo attivo
    state_manager.set("active_screen", "Main")
    
    print("System started successfully.\n")
    
    try:
        # Avvia il renderer CLI dello schermo
        render_screen(event_bus, state_manager)
            
    except KeyboardInterrupt:
        print("\nShutting down system...")
        print("System stopped cleanly.")

if __name__ == "__main__":
    main()