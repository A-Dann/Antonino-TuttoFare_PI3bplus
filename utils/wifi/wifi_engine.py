#!/usr/bin/env python3
"""
Wi-Fi Engine Module

Low-level management of Wi-Fi operations using NetworkManager (nmcli):
- Current status
- Nearby networks scan and smart connection (saved vs AP mode)
- Saved networks listing and removal
- Disconnection
"""

import subprocess
from config import TEMP_SELECTED_WIFI_INFO_JSON_PATH
from utils.file_utils import write_json

def get_current_connection_state():
    """Returns a dictionary with SSID, security, and signal of the currently connected network, or None."""
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "ACTIVE,SSID,SECURITY,SIGNAL", "dev", "wifi"],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("yes:"):
                parts = line.split(":")
                if len(parts) >= 4:
                    return {
                        "ssid": parts[1] if parts[1] else "Unknown",
                        "security": parts[2] if parts[2] else "Open",
                        "signal": parts[3] if parts[3] else "N/A"
                    }
        return None
    except Exception:
        return None

def scan_networks():
    """Scans for networks and returns a list of dictionaries with SSID and signal."""
    try:
        # 1. Force a fresh Wi-Fi scan to detect nearby networks
        subprocess.run(["nmcli", "device", "wifi", "rescan"], capture_output=True)
        
        # 2. Get the list of visible networks with clean output format
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SECURITY,SIGNAL", "dev", "wifi", "list"],
            capture_output=True, text=True, check=True
        )
        
        raw_networks = []
        
        # 3. Read the output and parse each line
        for line in result.stdout.splitlines():
            parts = line.split(":")
            if len(parts) >= 3:
                ssid = parts[0].strip()
                security = parts[1].strip()
                signal_strenght = parts[2].strip()

                if ssid and signal_strenght.isdigit():
                    raw_networks.append({
                        "ssid": ssid,
                        "security": security,
                        "signal": int(signal_strenght)})
        
        # 4. Sort by signal strength in descending order (highest signal first)
        raw_networks.sort(key=lambda x: x["signal"], reverse=True)
        
        networks = []
        seen = set()  # Used to filter out duplicate SSIDs (keeping the strongest one)
        
        # 5. Filter duplicates, keeping only the first occurrence (which now has the best signal)
        for net in raw_networks:
            if net["ssid"] not in seen:
                seen.add(net["ssid"])
                # Convert signal back to string if your frontend expects it
                net["signal"] = str(net["signal"])
                networks.append(net)
                    
        return networks
    except Exception:
        return []

def handle_network_selection(ssid, security):
    """
    Handles network selection.
    Returns:
        - "connected": Successfully connected to a saved or open network.
        - "ap_started": Successfully started the setup hotspot for a secured network.
        - "error": Something went wrong.
    """
    saved = get_saved_list()
    
    # 1. Saved network: connect directly
    if ssid in saved:
        try:
            subprocess.run(["nmcli", "connection", "up", ssid], capture_output=True, text=True, check=True)
            return "connected"
        except subprocess.CalledProcessError:
            return "error"
            
    # 2. Open network: connect directly without password
    elif not security or security == "--" or security.lower() == "open":
        try:
            subprocess.run(
                ["nmcli", "device", "wifi", "connect", ssid],
                capture_output=True, text=True, check=True
            )
            return "connected"
        except subprocess.CalledProcessError:
            return "error"
            
    # 3. Secured network: start AP mode for password configuration
    else:
        try:
            # Saves the chosen ssid in a temp json file
            write_json(TEMP_SELECTED_WIFI_INFO_JSON_PATH, {"ssid": ssid})

            # Desconnects the Pi's Wi-Fi
            subprocess.run(["nmcli", "device", "disconnect", "wlan0"], capture_output=True)

            # Starts temporary AP mode
            res = subprocess.run([
                "nmcli", "device", "wifi", "hotspot", 
                "ifname", "wlan0", 
                "ssid", "Ras-Pi_Input_Wi-Fi_Password", 
                "password", "12345678"
            ], capture_output=True, text=True)
            
            if res.returncode == 0:
                return "ap_started"
            else:
                return "error"
        except Exception:
            return "error"

def connect_with_saved_credentials(ssid, password):
    """Connects to a Wi-Fi network using the provided SSID and password."""
    try:
        result = subprocess.run(
            ["nmcli", "device", "wifi", "connect", ssid, "password", password],
            capture_output=True, text=True, check=True
        )
        return result.returncode == 0
    except Exception:
        return False

def get_saved_list():
    """Returns a clean list of saved Wi-Fi network names."""
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
            capture_output=True, text=True, check=True
        )
        networks = []
        for line in result.stdout.splitlines():
            parts = line.split(":")
            if len(parts) >= 2 and "wireless" in parts[1]:
                networks.append(parts[0])
        return networks
    except Exception:
        return []

def remove_network(target):
    """Removes a saved network from system-connections."""
    try:
        subprocess.run(["nmcli", "connection", "delete", target], capture_output=True, check=True)
        return True
    except Exception:
        return False

def disconnect_wifi():
    """Disconnects the Wi-Fi interface."""
    try:
        result = subprocess.run(["nmcli", "device", "disconnect", "wlan0"], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False