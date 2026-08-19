#!/usr/bin/env python3
"""
Wi-Fi Configuration Module

Manages Wi-Fi connections, saved networks removal, and AP mode activation
using NetworkManager (nmcli).
"""

import utils.wifi_engine as wifi_engine
from utils.i18n import t

def get_current_state():
    """
    Displays the current Wi-Fi state, including connection status,
    SSID, and IP address.
    """

    current = wifi_engine.get_current_state()
    if current:
        print(f"\nConnected to network: {current['ssid']}")
        print(f"Security: {current['security']}")
        print(f"Signal: {current['signal']}%")
    else:
        print(f"\nStatus: Disconnected.")

    #TODO IMPOSTA UNA MODALITA PREMI QUALSIASI BOTTONE
    input(f"\n{t('msg_press_enter_to_continue')} ")

def scan_and_connect():
    """
    Scans for available Wi-Fi networks and prompts the user to select one
    to connect to. If the selected network is secured, it will trigger AP mode.
    """

    # 1. Scan for available networks and display progress
    print(f"\n{t('wifi_scanning')}")
    networks = wifi_engine.scan_networks()

    # 2. Handle case where no networks are found
    if not networks:
        print(f"\n{t('wifi_no_networks_found')}")
        # TODO: SET A PRESS ANY KEY MODE
        input(f"\n{t('msg_press_enter_to_continue')} ")
        return

    # 3. Display the list of detected networks with index, security and signal
    print(f"\n--- {t('wifi_available_networks')} ({len(networks)}) ---")
    for idx, net in enumerate(networks, start=1):
        print(f"{idx}. {net['ssid']} ({t['wifi_security']}: {net['security']}%, {t('wifi_signal')}: {net['signal']})")
    
    # 4. Prompt the user to choose a network by its number
    choice = input(f"\n{t('wifi_select_network_prompt')} ").strip()
    if not choice.isdigit():
        print(f"\n{t'msg_unexpected_input'}")
        return
        
    # 5. Process the user selection and trigger connection logic
    selected_idx = int(choice) - 1
    if 0 <= selected_idx < len(networks):
        selected_net = networks[selected_idx]
        ssid = selected_net["ssid"]
        security = selected_net["security"]
        
        print(f"\n{t('wifi_connecting_to')} '{ssid}'...")
        status = wifi_engine.handle_network_selection(ssid, security)
        
        # 6. Check the status returned by the engine and show the appropriate message
        if status == "connected":
            print(f"\n{t('wifi_connected_successfully')}")
        elif status == "ap_started":
            # =========================================================================
            # TODO: [AP MODE ACTIVE - NEXT STEPS REQUIRED]
            # 1. The Wi-Fi hotspot has been successfully started.
            # 2. The screen is now frozen with the instructions for the user.
            # 3. WE NEED A WEB SERVER (e.g., Flask) running locally on the Raspberry Pi:
            #    - To intercept traffic or host a captive portal / local web page.
            #    - Where the user (connected via smartphone) can type the Wi-Fi password.
            # 4. Once the password is submitted by the user:
            #    - Tears down the hotspot, and re-enables standard Wi-Fi.
            #    - Read the target SSID from TEMP_WIFI_SSID_JSON_PATH.
            #    - CALL THE CONNECTION METHOD: A function in the backend (e.g., in wifi_engine) 
            #      that takes the saved SSID and the submitted password, runs the nmcli 
            #      connect comand to that Wi-Fi
            # =========================================================================
            handle_ap_mode_screen(ssid)
        else:
            print(f"\n{t('wifi_connection_error')}")
    else:
        print(f"\n{t('msg_invalid_choice')}")
        
    # TODO: SET A PRESS ANY KEY MODE
    input(f"\n{t('msg_press_enter_to_continue')} ")

def handle_ap_mode_screen(ssid):
    """
    Freezes the screen with dedicated instructions when AP mode is active,
    guiding the user to connect via smartphone and input the password.
    """
    print(f"\n" + "="*60)
    print(f" [!] {t('wifi_password_required').upper()}")
    print("="*60)
    print(f"\n1. {t('ap_step_1')}: Connect your device to Wi-Fi:")
    print(f"   SSID: Ras-Pi_Input_Wi-Fi_Password")
    print(f"   Password: 12345678")
    print(f"\n2. {t('ap_step_2')}: Open your browser and type the password")
    print(f"   for the target network: '{ssid}'")
    print(f"\n[i] {t('ap_waiting_instruction')}")
    print("="*60)
    
    # Keeps the screen frozen with instructions until the user presses Enter/key to exit
    # TODO: SET A PRESS ANY KEY MODE
    input(f"\n{t('msg_press_enter_to_continue')} ")

    # Optional: cleanup or disconnect the AP when exiting the screen
    wifi_engine.disconnect_wifi()

def get_saved_networks():
    """
    Lists all saved Wi-Fi networks on the device.
    """
    saved = wifi_engine.get_saved_list()
    print(f"\n--- {t('wifi_saved_networks')} ({len(saved)}) ---")
    if not saved:
        print(f"\n{t('wifi_no_saved_networks')}")
    else:
        for idx, net in enumerate(saved, start=1):
            print(f"{idx}. {net}")
            
    # TODO: SET A PRESS ANY KEY MODE
    input(f"\n{t('msg_press_enter_to_continue')} ")

def remove_saved_networks():
    """
    Prompts the user to select a saved Wi-Fi network to remove from the device.
    """
    saved = wifi_engine.get_saved_list()
    if not saved:
        print(f"\n{t('wifi_no_saved_to_remove')}")
        input(f"\n{t('msg_press_enter_to_continue')} ")
        return

    print(f"\n--- {t('wifi_remove_saved_title')} ---")
    for idx, net in enumerate(saved, start=1):
        print(f"{idx}. {net}")
        
    choice = input(f"\n{t('wifi_remove_select_prompt')} ").strip()
    if not choice.isdigit():
        print(f"\n{t('msg_unexpected_input')}")
        # TODO: SET A PRESS ANY KEY MODE
        input(f"\n{t('msg_press_enter_to_continue')} ")
        return
        
    selected_idx = int(choice) - 1
    if 0 <= selected_idx < len(saved):
        target = saved[selected_idx]
        success = wifi_engine.remove_network(target)
        if success:
            print(f"\n{t('wifi_remove_success')} '{target}'.")
        else:
            print(f"\n{t('wifi_remove_error')} '{target}'.")
    else:
        print(f"\n{t('msg_invalid_choice')}")
        
    # TODO: SET A PRESS ANY KEY MODE
    input(f"\n{t('msg_press_enter_to_continue')} ")

def disconnect_from_network():
    """
    Disconnects from the currently connected Wi-Fi network.
    """
    success = wifi_engine.disconnect_wifi()
    if success:
        print(f"\n{t('wifi_disconnect_success')}")
    else:
        print(f"\n{t('wifi_disconnect_error')}")
        
    # TODO: SET A PRESS ANY KEY MODE
    input(f"\n{t('msg_press_enter_to_continue')} ")

def run():
    while True:
        print(f"\n--- {t('wifi_title')} ---")
        print(f"1. {t('configure_get_current_state')}")
        print(f"2. {t('configure_scan_and_connect')}")
        print(f"3. {t('configure_get_saved_networks')}")
        print(f"4. {t('configure_remove_saved_networks')}")
        print(f"5. {t('configure_disconnect_from_network')}")
        print(f"6. {t('msg_back_to_settings')}")

        choice = input(f"{t('settings_prompt_choice')} ").strip()

        if choice == '1':
            get_current_state()
        elif choice == '2':
            scan_and_connect()
        elif choice == '3':
            get_saved_networks()
        elif choice == '4':
            remove_saved_networks()
        elif choice == '5':
            disconnect_from_network()
        elif choice == '6':
            print(t('msg_back_to_menu'))
            return
        else:
            print(t('msg_invalid_choice'))