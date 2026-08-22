#!/usr/bin/env python3
"""
Wi-Fi Configuration Module

Manages Wi-Fi connections, saved networks removal, and AP mode activation
using NetworkManager (nmcli).
"""

import subprocess
import sys
import time
import pygame
from graphic.menu_renderer import render_menu
from graphic.ui_components import show_message_screen
from utils.file_utils import read_json
from utils.i18n import t

import utils.wifi.wifi_engine as wifi_engine
from config import CAPTIVE_PORTAL_SCRIPT_PATH, TEMP_SELECTED_WIFI_INFO_JSON_PATH


def get_current_state():
    """
    Displays the current Wi-Fi state, including connection status,
    SSID, and IP address.
    """

    current = wifi_engine.get_current_connection_state()
    if current:
        print(f"\n{t('key_connected_to')}: {current['ssid']}")
        print(f"{t('key_security')}: {current['security']}")
        print(f"{t('key_signal')}: {current['signal']}%")
    else:
        print(f"\n{t('configure_wifi_status_disconnected')}")

    #TODO IMPOSTA UNA MODALITA PREMI QUALSIASI BOTTONE
    input(f"\n{t('msg_press_enter_to_continue')} ")

def scan_and_connect():
    """
    Scans for available Wi-Fi networks and prompts the user to select one
    to connect to. If the selected network is secured, it will trigger AP mode.
    """

    # 1. Scan for available networks and display progress
    print(f"\n{t('configure_wifi_scanning')}")
    networks = wifi_engine.scan_networks()

    # 2. Handle case where no networks are found
    if not networks:
        print(f"\n{t('configure_wifi_no_networks_found')}")
        # TODO: SET A PRESS ANY KEY MODE
        input(f"\n{t('msg_press_enter_to_continue')} ")
        return

    # 3. Display the list of detected networks with index, security and signal
    print(f"\n--- {t('configure_wifi_available_networks')} ({len(networks)}) ---")
    for idx, net in enumerate(networks, start=1):
        print(f"{idx}. {net['ssid']} ({t('key_security')}: {net['security']}%, {t('key_signal')}: {net['signal']})")
    
    # 4. Prompt the user to choose a network by its number
    choice = input(f"\n{t('configure_wifi_select_network')} ").strip()
    if not choice.isdigit():
        print(f"\n{t('msg_unexpected_input')}")
        return
        
    # 5. Process the user selection and trigger connection logic
    selected_idx = int(choice) - 1
    if 0 <= selected_idx < len(networks):
        selected_net = networks[selected_idx]
        ssid = selected_net["ssid"]
        security = selected_net["security"]
        
        print(f"\n{t('configure_wifi_connecting_to')} '{ssid}'...")
        status = wifi_engine.handle_network_selection(ssid, security)
        
        # 6. Check the status returned by the engine and show the appropriate message
        if status == "connected":
            print(f"\n{t('configure_wifi_connected_successfully')}")
        elif status == "ap_started":
            print(f"\n{t('configure_wifi_password_required_start_ap')}")
            run_ap_mode_session(ssid)
        else:
            print(f"\n{t('configure_wifi_connection_error')}")
    else:
        print(f"\n{t('msg_invalid_choice')}")
        
    # TODO: SET A PRESS ANY KEY MODE
    input(f"\n{t('msg_press_enter_to_continue')} ")

def run_ap_mode_session(ssid):
    """
    Manages the AP mode session: runs the captive portal, waits for completion,
    checks for saved credentials, and triggers either connection or error handling.
    """

    while True:
        # 1. Start the Flask captive portal server
        flask_process = subprocess.Popen(["sudo", "python3", CAPTIVE_PORTAL_SCRIPT_PATH])    

        try:
            #TODO WRITE THE FREEZE SCREEN WITH THE INSTRUCCIONS ON HOW TO CONNECT:
            # This text should be translated based on the system language choices
            # Turn on your device's wi-fi:
            # Connect to: Ras-Pi_Input_Wi-Fi_Password
            # Password: 12345678
            # Type the password and press Submit
            # Press any key to exit ap mode
            
            # Set a 5-minute timeout (300 seconds)
            timeout_seconds = 300
            start_time = time.time()

            while flask_process.poll() is None:
                # Check if 5 minutes have elapsed
                if time.time() - start_time > timeout_seconds:
                    if flask_process.poll() is None:
                        flask_process.terminate()
                        flask_process.wait()
                    print(f"\n{t('configure_wifi_ap_timeout')}") #has no key of translation
                    break

                time.sleep(0.5)
            
        except KeyboardInterrupt:
            if flask_process.poll() is None:
                flask_process.terminate()
                flask_process.wait()
            wifi_engine.disconnect_wifi()
            return

        # 2. Flask has closed (5 seconds passed)
        # Now check if the password was correctly stored in the JSON file.
        data = read_json(TEMP_SELECTED_WIFI_INFO_JSON_PATH)
        saved_password = data.get("password") if data else None

        # 3. Control check: did the user actually submit a password?
        if saved_password:
            print(f"\n{t('configure_wifi_connecting_to')} '{ssid}'...")
            wifi_engine.disconnect_wifi()

            # TODO: Mostra schermata "Connessione in corso..."
            success = wifi_engine.connect_with_saved_credentials(ssid, saved_password)

            if success:
                print(f"\n{t('configure_wifi_connected_successfully')}")
            else:
                print(f"\n{t('configure_wifi_connection_error')}")
            break
        else:
            # No password found or json file corrupted
            print(f"\n{t('configure_wifi_no_password_found')}")

            # Ask the user if they want to retry or exit
            choice = input(f"\n{t('configure_wifi_ask_for_retry')}").strip().lower()
            if choice != 'y':
                wifi_engine.disconnect_wifi()
                print(f"\n{t('configure_wifi_back_to_wifi_menu')}")
                break

            # If 'y', the loop restarts and launches Flask again.


def get_saved_networks():
    """
    Lists all saved Wi-Fi networks on the device.
    """
    saved = wifi_engine.get_saved_list()
    print(f"\n--- {t('configure_wifi_saved_networks_label')} ({len(saved)}) ---")
    if not saved:
        print(f"\n{t('configure_wifi_no_saved_networks_found')}")
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
        print(f"\n{t('configure_wifi_no_saved_networks_found')}")
        input(f"\n{t('msg_press_enter_to_continue')} ")
        return

    print(f"\n--- {t('configure_wifi_remove_saved_networks_label')} ---")
    for idx, net in enumerate(saved, start=1):
        print(f"{idx}. {net}")
        
    choice = input(f"\n{t('configure_wifi_select_network_to_remove')} ").strip()
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
            print(f"\n{t('configure_wifi_network_removed_successfully')} '{target}'.")
        else:
            print(f"\n{t('configure_wifi_remove_network_error')} '{target}'.")
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
        print(f"\n{t('configure_wifi_disconnected_successfully')}")
    else:
        print(f"\n{t('configure_wifi_disconnection_error')}")
        
    # TODO: SET A PRESS ANY KEY MODE
    input(f"\n{t('msg_press_enter_to_continue')} ")

def offline_online_mode():
    ""
    #TODO WORK IN PROGRESS

def draw_frame(virtual_screen, selected_index=0, events=None):
    """
    Renders a single frame of the Wi-Fi configuration menu using passed events.
    """

    # 1. Define translated options for the Wi-Fi configuration menu
    configure_wifi_options = [
        t('configure_wifi_get_current_state'),
        t('configure_wifi_scan_and_connect'),
        t('configure_wifi_get_saved_networks'),
        t('configure_wifi_remove_saved_networks'),
        t('configure_wifi_disconnect_from_network'),
        t('configure_wifi_offline_online_mode'),
        t('configure_wifi_back_to_settings')
    ]

    # 2. Fallback event fetching if none are passed from the main loop
    if events is None:
        events = pygame.event.get()

    # 3. Process keyboard input events
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                # Move selection down (cyclic)
                selected_index = (selected_index + 1) % len(configure_wifi_options)
            elif event.key == pygame.K_UP:
                # Move selection up (cyclic)
                selected_index = (selected_index - 1) % len(configure_wifi_options)
            elif event.key == pygame.K_RETURN:
                # Handle selection confirmation on options by calling the respective functions
                if selected_index == 0:
                    get_current_state()
                elif selected_index == 1:
                    scan_and_connect()
                elif selected_index == 2:
                    get_saved_networks()
                elif selected_index == 3:
                    remove_saved_networks()
                elif selected_index == 4:
                    disconnect_from_network()
                elif selected_index == 5:
                    offline_online_mode()
                elif selected_index == 6:
                    return "SETTINGS", selected_index

            elif event.key == pygame.K_ESCAPE:
                # Quick return to settings using ESC
                return "SETTINGS", selected_index

    # 4. Render the current frame graphics
    render_menu(
        screen=virtual_screen,
        menu_title=t('configure_wifi_title'),
        menu_options=configure_wifi_options,
        selected_index=selected_index
    )

    # 5. Return the active state and current index back to the main loop
    return "CONFIGURE_WIFI", selected_index