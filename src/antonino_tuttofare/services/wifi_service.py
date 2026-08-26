#!/usr/env/python3
"""
Wi-Fi Service Module

Handles business logic for Wi-Fi operations, including scanning, connection handling,
captive portal AP mode execution, and saved networks management.
"""

import subprocess
import sys
import time

from antonino_tuttofare.config import PROJECT_ROOT, TEMP_SELECTED_WIFI_INFO_JSON_PATH
import antonino_tuttofare.hardware.wifi_engine as wifi_engine
from antonino_tuttofare.utility.files_utils import read_json
from antonino_tuttofare.utility.logger import get_logger

logger = get_logger(__name__)


def get_current_connection_info() -> dict | None:
    """Retrieve current Wi-Fi connection state."""
    try:
        return wifi_engine.get_current_connection_state()
    except Exception as e:
        logger.error(f"Failed to retrieve current Wi-Fi state: {e}")
        return None


def scan_available_networks() -> list:
    """Scan and return available Wi-Fi networks."""
    try:
        return wifi_engine.scan_networks() or []
    except Exception as e:
        logger.error(f"Error during network scan execution: {e}")
        return []


def connect_to_network(ssid: str, security: str) -> str:
    """
    Handle connection to a selected network.
    Returns: 'connected', 'ap_required', or 'error'
    """
    try:
        logger.info(f"Handling connection for network: '{ssid}' with security: {security}")
        return wifi_engine.handle_network_selection(ssid, security)
    except Exception as e:
        logger.error(f"Failed to connect to network '{ssid}': {e}")
        return "error"


def run_ap_mode_session(ssid: str) -> str:
    """
    Manages the AP mode session, captive portal process, and credential submission.
    Returns: 'connected', 'retry', or 'aborted'
    """
    logger.debug(f"Starting AP mode session for target SSID: '{ssid}'")
    
    while True:
        try:
            if wifi_engine.start_ap_mode() != "ap_started":
                logger.error("Failed to start Wi-Fi Access Point mode.")
                return "error"

            logger.info("Launching Flask captive portal server process...")
            flask_process = subprocess.Popen(
                [sys.executable, "-m", "utils.wifi.wifi_captive_portal_engine"],
                cwd=PROJECT_ROOT
            )

            deadline = time.monotonic() + 300  # 5-minute timeout

            while flask_process.poll() is None:
                if time.monotonic() > deadline:
                    logger.warning("Captive portal session timed out after 5 minutes.")
                    flask_process.terminate()
                    flask_process.wait()
                    break
                time.sleep(1)

            logger.debug("Shutting down AP mode and disconnecting interface to apply credentials...")
            wifi_engine.disconnect_wifi()

            data = read_json(TEMP_SELECTED_WIFI_INFO_JSON_PATH) or {}
            saved_password = data.get("password")

            if saved_password:
                logger.info(f"Retrieved saved credentials from captive portal for SSID: '{ssid}'")
                success = wifi_engine.connect_with_saved_credentials(ssid, saved_password)
                if success:
                    logger.info(f"Successfully connected to '{ssid}' using captive portal credentials.")
                    return "connected"
                else:
                    logger.warning(f"Connection attempt failed using captive portal credentials for '{ssid}'.")
                    return "retry_prompt"
            else:
                logger.warning("No password found or configuration file missing after AP session.")
                return "retry_prompt"

        except Exception as e:
            logger.error(f"Unexpected error during AP mode session: {e}")
            return "error"


def get_saved_networks_list() -> list:
    """Retrieve list of saved networks."""
    try:
        return wifi_engine.get_saved_list() or []
    except Exception as e:
        logger.error(f"Failed to retrieve saved networks: {e}")
        return []


def remove_saved_network(target: str) -> bool:
    """Remove a specific saved network profile."""
    try:
        logger.info(f"Attempting to remove saved network profile: '{target}'")
        return wifi_engine.remove_network(target)
    except Exception as e:
        logger.error(f"Failed to remove network profile '{target}': {e}")
        return False


def disconnect_current_network() -> bool:
    """Disconnect from active Wi-Fi."""
    try:
        logger.info("Executing manual Wi-Fi disconnection request...")
        return wifi_engine.disconnect_wifi()
    except Exception as e:
        logger.error(f"Unexpected error during Wi-Fi disconnection: {e}")
        return False