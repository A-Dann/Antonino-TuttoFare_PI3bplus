#!/usr/bin/env python3
"""
Wi-Fi Configuration Module (CLI State Version)

Provides the interactive CLI user interface for Wi-Fi management adapted
for the state machine architecture, delegating operations to wifi_service.
"""

from antonino_tuttofare.utility.i18n import t
from antonino_tuttofare.utility.logger import get_logger
import antonino_tuttofare.services.wifi_service as wifi_service

logger = get_logger(__name__)


def show_current_state() -> None:
    """Displays the current Wi-Fi state."""
    logger.debug("Displaying current Wi-Fi state via menu...")
    current = wifi_service.get_current_connection_info()
    
    if current:
        print(f"\n{t('key_connected_to')}: {current['ssid']}")
        print(f"{t('key_security')}: {current['security']}")
        print(f"{t('key_signal')}: {current['signal']}%")
    else:
        print(f"\n{t('configure_wifi_status_disconnected')}")

    input(f"\n{t('msg_press_enter_to_continue')} ")


def handle_scan_and_connect() -> None:
    """Handles network scanning and user selection loop."""
    logger.info("Initiating Wi-Fi scan and connect menu flow...")
    print(f"\n{t('configure_wifi_scanning')}")
    
    networks = wifi_service.scan_available_networks()
    if not networks:
        print(f"\n{t('configure_wifi_no_networks_found')}")
        input(f"\n{t('msg_press_enter_to_continue')} ")
        return

    print(f"\n--- {t('configure_wifi_available_networks')} ({len(networks)}) ---")
    for idx, net in enumerate(networks, start=1):
        print(f"{idx}. {net['ssid']} ({t('key_security')}: {net['security']}%, {t('key_signal')}: {net['signal']})")
    
    choice = input(f"\n{t('configure_wifi_select_network')} ").strip()
    if not choice.isdigit():
        print(f"\n{t('msg_unexpected_input')}")
        input(f"\n{t('msg_press_enter_to_continue')} ")
        return
        
    selected_idx = int(choice) - 1
    if 0 <= selected_idx < len(networks):
        selected_net = networks[selected_idx]
        ssid = selected_net["ssid"]
        security = selected_net["security"]
        
        print(f"\n{t('configure_wifi_connecting_to')} '{ssid}'...")
        status = wifi_service.connect_to_network(ssid, security)
        
        if status == "connected":
            print(f"\n{t('configure_wifi_connected_successfully')}")
        elif status == "ap_required":
            print(f"\n{t('configure_wifi_password_required_start_ap')}")

            # Run AP mode session loop with retry options
            while True:
                ap_result = wifi_service.run_ap_mode_session(ssid)
                if ap_result == "connected":
                    print(f"\n{t('configure_wifi_connected_successfully')}")
                    break
                elif ap_result == "retry_prompt":
                    retry_choice = input(f"\n{t('configure_wifi_ask_for_retry')}").strip().lower()
                    if retry_choice == 'y':
                        continue
                    else:
                        break
                else:
                    print(f"\n{t('configure_wifi_connection_error')}")
                    break
            print(f"\n{t('configure_wifi_back_to_wifi_menu')}")
        else:
            print(f"\n{t('configure_wifi_connection_error')}")
    else:
        print(f"\n{t('msg_invalid_choice')}")
        
    input(f"\n{t('msg_press_enter_to_continue')} ")


def show_saved_networks() -> None:
    """Displays saved networks list."""
    saved = wifi_service.get_saved_networks_list()
    print(f"\n--- {t('configure_wifi_saved_networks_label')} ({len(saved)}) ---")
    
    if not saved:
        print(f"\n{t('configure_wifi_no_saved_networks_found')}")
    else:
        print(f"\n{t('configure_wifi_no_saved_networks_found')}") if not saved else None
        for idx, net in enumerate(saved, start=1):
            print(f"{idx}. {net}")
            
    input(f"\n{t('msg_press_enter_to_continue')} ")


def handle_remove_saved_network() -> None:
    """Handles removal of a saved network profile."""
    saved = wifi_service.get_saved_networks_list()
    if not saved:
        print(f"\n{t('configure_wifi_no_saved_networks_found')}")
        input(f"\n{t('msg_press_enter_to_continue')} ")
        return

    print(f"\n--- {t('configure_wifi_remove_saved_networks_label')} ---")
    for idx, net in enumerate(saved, start=1):
        print(f"{idx}. {net}")
        
    choice = input(f"\n{t('configure_wifi_select_network_to_remove')} ").strip()
    if not choice.isdigit():
        print(f"\n{t('msg_unexpected_input')}")
        input(f"\n{t('msg_press_enter_to_continue')} ")
        return
        
    selected_idx = int(choice) - 1
    if 0 <= selected_idx < len(saved):
        target = saved[selected_idx]
        success = wifi_service.remove_saved_network(target)
        if success:
            print(f"\n{t('configure_wifi_network_removed_successfully')} '{target}'.")
        else:
            print(f"\n{t('configure_wifi_remove_network_error')} '{target}'.")
    else:
        print(f"\n{t('msg_invalid_choice')}")
        
    input(f"\n{t('msg_press_enter_to_continue')} ")


def handle_disconnection() -> None:
    """Disconnects from active Wi-Fi network."""
    success = wifi_service.disconnect_current_network()
    if success:
        print(f"\n{t('configure_wifi_disconnected_successfully')}")
    else:
        print(f"\n{t('configure_wifi_disconnection_error')}")
        
    input(f"\n{t('msg_press_enter_to_continue')} ")


def run_cli_state(selected_index=0):
    """
    Renders the Wi-Fi configuration menu once in the terminal, processes a single choice input,
    and returns the next application state and selected index.
    """
    print(f"\n--- {t('configure_wifi_title')} ---")
    print(f"1. {t('configure_wifi_get_current_state')}")
    print(f"2. {t('configure_wifi_scan_and_connect')}")
    print(f"3. {t('configure_wifi_get_saved_networks')}")
    print(f"4. {t('configure_wifi_remove_saved_networks')}")
    print(f"5. {t('configure_wifi_disconnect_from_network')}")
    print(f"6. {t('configure_wifi_back_to_settings')}")

    choice = input(f"{t('msg_prompt_choice')} ").strip()

    if choice == '1':
        show_current_state()
        return "WIFI_MENU", selected_index
    elif choice == '2':
        handle_scan_and_connect()
        return "WIFI_MENU", selected_index
    elif choice == '3':
        show_saved_networks()
        return "WIFI_MENU", selected_index
    elif choice == '4':
        handle_remove_saved_network()
        return "WIFI_MENU", selected_index
    elif choice == '5':
        handle_disconnection()
        return "WIFI_MENU", selected_index
    elif choice == '6':
        print(t('msg_back_to_menu'))
        logger.info("Returning to Settings.")
        return "SETTINGS", selected_index
    else:
        print(t('msg_invalid_choice'))
        logger.warning("Invalid Wi-Fi menu choice entered: %s", choice)
        return "WIFI_MENU", selected_index