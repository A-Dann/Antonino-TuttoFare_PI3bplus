#!/usr/bin/env python3
"""
Wi-Fi Engine Module

Low-level management of Wi-Fi operations using NetworkManager (nmcli):
- Current status check.
- Nearby networks scan and smart connection (handling saved, open, or AP mode).
- Saved networks listing (with automatic stripping of Netplan system-connection prefixes).
- Network removal and explicit profile resolution.
- Disconnection management.

Raspberry Pi Connectivity Architecture:
- Uses NetworkManager as the primary backend daemon for network interfaces (wlan0).
- Interacts with netplan-generated system profiles (e.g., netplan-wlan0-SSID) 
  where NetworkManager relies on configuration persistence layers.
- Supports standard wireless protocols (802.11 b/g/n/ac depending on hardware) 
  and fallback mechanisms between Infrastructure mode (client) and Access Point (AP) mode.
"""

import subprocess
from src.antonino_tuttofare.config import TEMP_SELECTED_WIFI_INFO_JSON_PATH
from antonino_tuttofare.utility.files_utils import write_json
from antonino_tuttofare.utility.logger import get_logger

logger = get_logger(__name__)

def get_current_connection_state():
    """
    Checks if the Raspberry Pi is currently connected to a Wi-Fi network.
    Returns a dictionary with SSID, security, and signal strength, or None if not connected.
    """

    logger.debug("Checking current Wi-Fi connection state via NetworkManager...")
    try:
        # Query NetworkManager for Wi-Fi device status in tabular format
        result = subprocess.run(
            ["nmcli", "-t", "-f", "ACTIVE,SSID,SECURITY,SIGNAL", "dev", "wifi"],
            capture_output=True, text=True, check=True
        )

        # Parse output line by line searching for the active connection (indicated by "yes:")
        for line in result.stdout.splitlines():
            if line.startswith("yes:"):
                parts = line.split(":")
                if len(parts) >= 4:
                    connection_info = {
                        "ssid": parts[1] if parts[1] else "Unknown",
                        "security": parts[2] if parts[2] else "Open",
                        "signal": parts[3] if parts[3] else "N/A"
                    }
                    logger.info(f"Active Wi-Fi connection found: {connection_info['ssid']}")
                    return connection_info
        logger.debug("No active Wi-Fi connection found.")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to query Wi-Fi status via nmcli: {e.stderr.strip()}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while checking Wi-Fi connection state: {e}")
        return None

def scan_networks():
    """
    Forces a fresh Wi-Fi scan via NetworkManager and returns a sorted list 
    of dictionaries containing SSID, security, and signal strength (without duplicates).
    """ 
    logger.info("Initiating forced Wi-Fi network scan...")
    try:
        # Trigger a rescan and get the list of visible networks
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SECURITY,SIGNAL", "dev", "wifi", "list", "--rescan", "yes"],
            capture_output=True, text=True, check=True
        )

        raw_networks = []
        
        # Parse each line returned by nmcli
        for line in result.stdout.splitlines():
            parts = line.split(":")
            if len(parts) >= 3:
                ssid = parts[0].strip()
                security = parts[1].strip()
                signal_strength = parts[2].strip()

                # Filter only valid networks with a non-empty SSID and numeric signal
                if ssid and signal_strength.isdigit():
                    raw_networks.append({
                        "ssid": ssid,
                        "security": security if security else "Open",
                        "signal": int(signal_strength)
                    })
        
        # Sort networks from strongest to weakest signal
        raw_networks.sort(key=lambda x: x["signal"], reverse=True)
        
        networks = []
        seen = set()  # Used to filter out duplicates (keeping the strongest signal occurrence)
        
        for net in raw_networks:
            if net["ssid"] not in seen:
                seen.add(net["ssid"])
                net["signal"] = str(net["signal"])  # Convert signal back to string for frontend compatibility
                networks.append(net)

        logger.info(f"Wi-Fi scan completed successfully. Found {len(networks)} unique networks.")
        return networks
    except subprocess.CalledProcessError as e:
        logger.error(f"Wi-Fi scan failed via nmcli: {e.stderr.strip()}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during Wi-Fi scan: {e}")
        return []

def handle_network_selection(ssid, security):
    """
    Handles user network selection.
    Returns:
        - "connected": Successfully connected to a saved or open network.
        - "ap_required": The network is secured and requires AP mode to gather the password.
        - "error": Something went wrong.
    """
    logger.info(f"Handling network selection for SSID: '{ssid}' (Security: {security})")
    saved = get_saved_list()
    
    # CASE 1: The network is already saved in the system -> Connect directly
    if ssid in saved:
        logger.debug(f"Network '{ssid}' is found in saved profiles. Attempting direct connection.")
        try:
            # Query NetworkManager for all existing connection profiles to resolve Netplan naming conventions
            profiles_res = subprocess.run(
                ["nmcli", "-t", "-f", "NAME", "connection", "show"],
                capture_output=True, text=True, check=True
            )
            profile_to_up = ssid
            for line in profiles_res.stdout.splitlines():
                p_name = line.strip()
                # Handle both plain SSIDs and Netplan-prefixed system profiles
                if p_name == ssid or p_name == f"netplan-wlan0-{ssid}":
                    profile_to_up = p_name
                    break
                
            # Bring up the matched connection profile
            subprocess.run(
                ["nmcli", "connection", "up", profile_to_up],
                capture_output=True, text=True, check=True)
            logger.info(f"Successfully connected to saved network profile: '{profile_to_up}'")
            return "connected"
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to connect to saved network '{ssid}': {e.stderr.strip()}")
            return "error"
            
    # CASE 2: The network is open (no password) -> Connect directly without credentials
    elif not security or security == "--" or security.lower() == "open":
        logger.debug(f"Network '{ssid}' is open. Attempting direct connection without credentials.")
        try:
            subprocess.run(
                ["nmcli", "device", "wifi", "connect", ssid],
                capture_output=True, text=True, check=True
            )
            logger.info(f"Successfully connected to open network: '{ssid}'")
            return "connected"
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to connect to open network '{ssid}': {e.stderr.strip()}")
            return "error"
        
    # CASE 3: The network is secured and not saved -> Save SSID to temporary file and trigger AP mode
    else:
        logger.info(f"Network '{ssid}' is secured and not saved. Storing target SSID and requesting AP mode.")
        if write_json(TEMP_SELECTED_WIFI_INFO_JSON_PATH, {"ssid": ssid}):
            return "ap_required"
        else:
            logger.error(f"Failed to write temporary SSID file for '{ssid}'")
            return "error"

def start_ap_mode():
    """
    Starts Access Point (Hotspot) mode on the Raspberry Pi so the user's smartphone 
    can connect and provide the Wi-Fi password for the target network.
    """
    logger.info("Starting Access Point (AP) mode...")
    try:
        # Disconnect wlan0 to free up the interface and prevent conflicts
        subprocess.run(["nmcli", "device", "disconnect", "wlan0"],
            capture_output=True)

        # Configure and start NetworkManager's native hotspot mode
        result = subprocess.run(
            ["nmcli", "device", "wifi", "hotspot", "ifname", "wlan0", "ssid", "Ras-Pi_Input_Wi-Fi_Password", "password", "12345678"],
            capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("Access Point mode started successfully ('Ras-Pi_Input_Wi-Fi_Password').")
            return "ap_started"
        else:
            logger.error(f"Failed to start Access Point mode: {result.stderr.strip()}")
            return "error"
    except Exception as e:
        logger.error(f"Unexpected error while starting AP mode: {e}")
        return "error"

def connect_with_saved_credentials(ssid, password):
    """Connects to a Wi-Fi network using the provided SSID and password."""
    logger.info(f"Attempting to connect to secured network '{ssid}' using provided credentials...")
    try:
        result = subprocess.run(
            ["nmcli", "device", "wifi", "connect", ssid, "password", password],
            capture_output=True, text=True, check=True
        )
        success = result.returncode == 0
        if success:
            logger.info(f"Successfully connected to network '{ssid}' with credentials.")
        else:
            logger.warning(f"Connection attempt to '{ssid}' returned non-zero code.")
        return success
    except subprocess.CalledProcessError as e:
        logger.error(f"Authentication or connection failure for '{ssid}': {e.stderr.strip()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while connecting to '{ssid}': {e}")
        return False

def get_saved_list():
    """Returns a clean list of saved Wi-Fi network names."""
    logger.debug("Retrieving list of saved Wi-Fi networks...")
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
            capture_output=True, text=True, check=True
        )
        networks = []
        for line in result.stdout.splitlines():
            parts = line.split(":")
            if len(parts) >= 2 and "wireless" in parts[1]:
                name = parts[0]
                # Strip the Netplan system prefix to expose a clean, user-friendly SSID string
                if name.startswith("netplan-wlan0-"):
                    name = name.replace("netplan-wlan0-", "", 1)
                networks.append(name)
        logger.debug(f"Retrieved {len(networks)} saved wireless profiles.")
        return networks
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to retrieve saved network list: {e.stderr.strip()}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while fetching saved networks: {e}")
        return []

def remove_network(target):
    """Removes a saved network from system-connections."""
    logger.info(f"Request to remove saved network profile: '{target}'")
    try:
        # Retrieve all connection profile names from NetworkManager to locate the correct target
        result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME", "connection", "show"],
            capture_output=True, text=True, check=True
        )

        profile_to_delete = target
        for line in result.stdout.splitlines():
            profile_name = line.strip()
            # Match target against raw profile name or Netplan-prefixed system profile name
            if profile_name == target or profile_name == f"netplan-wlan0-{target}":
                profile_to_delete = profile_name
                break

        # Delete the resolved connection profile from system storage
        subprocess.run(["nmcli", "connection", "delete", profile_to_delete],
                       capture_output=True, check=True)
        logger.info(f"Successfully removed network profile: '{profile_to_delete}'")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to remove network profile '{target}': {e.stderr.strip()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while removing network '{target}': {e}")
        return False

def disconnect_wifi():
    """Disconnects the Wi-Fi interface."""
    logger.info("Disconnecting wlan0 interface...")
    try:
        result = subprocess.run(["nmcli", "device", "disconnect", "wlan0"], capture_output=True, text=True)
        success = result.returncode == 0
        if success:
            logger.info("wlan0 disconnected successfully.")
        else:
            logger.warning(f"Disconnect command returned non-zero code: {result.stderr.strip()}")
        return success
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to disconnect wlan0: {e.stderr.strip()}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during wlan0 disconnection: {e}")
        return False