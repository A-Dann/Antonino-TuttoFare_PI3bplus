#!/usr/init/env python3
"""
Sync Engine Module

This module handles network connectivity checks, automatic reconnection via NetworkManager,
high-precision Wi-Fi geolocation using the Google Geolocation API, reverse geocoding via OpenStreetMap,
IP-based location as fallback, system timezone updates, and local configuration persistence.
"""

import os
import json
import datetime
import subprocess
import time
import requests

from antonino_tuttofare import config
from antonino_tuttofare.utility.i18n import t
from antonino_tuttofare.utility.logger import get_logger

logger = get_logger(__name__)


def check_internet_connection() -> bool:
    """
    Check for internet connectivity by pinging an external reliable endpoint.

    Returns:
        bool: True if internet is reachable (HTTP 200), False otherwise.
    """
    logger.debug("Checking internet connectivity via external HTTP request...")
    try:
        response = requests.get("https://www.google.com", timeout=5)
        is_connected = response.status_code == 200
        if is_connected:
            logger.debug("Internet connection is active and reachable.")
        else:
            logger.warning(f"Internet check returned status code: {response.status_code}")
        return is_connected
    except requests.RequestException as e:
        logger.warning(f"Internet connection check failed: {e}")
        return False


def try_connection_to_known_networks() -> bool:
    """
    Attempt automatic reconnection to known Wi-Fi networks using NetworkManager.

    Returns:
        bool: True if connection is successfully established, False otherwise.
    """
    logger.info(t('sync_engine_currently_offline'))
    try:
        logger.debug("Enabling NetworkManager networking interface...")
        subprocess.run(["nmcli", "networking", "on"], capture_output=True, text=True)
        time.sleep(5)
        return check_internet_connection()
    except Exception as e:
        logger.error(f"Unexpected error while attempting automatic reconnection: {e}")
        return False


def has_wifi_hardware() -> bool:
    """
    Check if the system has a functional Wi-Fi interface for high-precision scanning.

    Returns:
        bool: True if a Wi-Fi device is present, False otherwise.
    """
    logger.debug("Checking for available Wi-Fi hardware interfaces...")
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "TYPE", "dev"],
            capture_output=True,
            text=True,
            check=True
        )
        has_wifi = "wifi" in result.stdout.lower()
        logger.debug(f"Wi-Fi hardware presence detected: {has_wifi}")
        return has_wifi
    except Exception as e:
        logger.error(f"Failed to check Wi-Fi hardware status: {e}")
        return False


def scan_wifi_networks() -> list:
    """
    Scan nearby Wi-Fi networks and extract their MAC addresses and signal strengths.

    Returns:
        list[dict]: A list of dictionaries containing 'macAddress' and 'signalStrength'.
    """
    if not has_wifi_hardware():
        logger.debug("Skipping Wi-Fi scan: no wireless hardware available.")
        return []

    logger.debug("Scanning nearby Wi-Fi networks for geolocation...")
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "BSSID,SIGNAL", "dev", "wifi"],
            capture_output=True,
            text=True,
            check=True
        )
        
        networks = []
        for line in result.stdout.splitlines():
            parts = line.split(":")

            if len(parts) >= 6:
                bssid = ":".join(parts[:6])
                signal = parts[-1]

                if bssid and bssid != "--":
                    try:
                        networks.append({
                            "macAddress": bssid,
                            "signalStrength": int(signal)
                        })
                    except ValueError:
                        continue
        
        logger.debug(f"Successfully collected {len(networks)} Wi-Fi access points for geolocation.")
        return networks
    except Exception as e:
        logger.error(t('sync_engine_wifi_scan_error').format(e=e))
        return []


def fetch_location_from_wifi() -> tuple:
    """
    Use Google Geolocation API via nearby Wi-Fi networks to get precise coordinates.

    Returns:
        tuple[float, float] | None: A tuple containing (latitude, longitude), or None if it fails.
    """
    wifi_list = scan_wifi_networks()
    if not wifi_list:
        return None

    api_key = getattr(config, "GOOGLE_API_KEY", "")
    if not api_key:
        logger.error("Google API Key is missing in configuration. Cannot query Google Geolocation API.")
        return None

    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}"
    payload = {
        "wifiAccessPoints": wifi_list
    }
    
    logger.debug("Sending Wi-Fi fingerprint to Google Geolocation API...")
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            lat = data.get("location", {}).get("lat")
            lng = data.get("location", {}).get("lng")

            if lat and lng:
                logger.debug(f"Google resolved coordinates: Lat {lat}, Lng {lng}")
                return lat, lng
        else:
            logger.warning(f"Google Geolocation API returned status code: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        logger.error(f"Google Geolocation error: {e}")
    
    return None


def get_city_from_coords(lat: float, lng: float) -> tuple:
    """
    Convert latitude and longitude into a city and country name via OpenStreetMap Nominatim.

    Args:
        lat (float): Latitude coordinate.
        lng (float): Longitude coordinate.

    Returns:
        tuple[str | None, str | None]: A tuple containing (city_name, country_name) or (None, None).
    """
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}"
    headers = {'User-Agent': 'RaspberryPiLocationSync/1.0'}
    
    logger.debug(f"Performing reverse geocoding via OpenStreetMap for coordinates ({lat}, {lng})...")
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})

            city = address.get("city") or address.get("town") or address.get("village") or address.get("municipality")
            country = address.get("country")

            logger.debug(f"Reverse geocoding resolved - City: {city}, Country: {country}")
            return city, country
        else:
            logger.warning(f"OpenStreetMap Nominatim returned status code: {response.status_code}")
    except requests.RequestException as e:
        logger.error(t('sync_engine_nominatim_error').format(e=e))
    
    return None, None


def fetch_location_fallback_ip() -> dict:
    """
    Retrieve location data based on public IP as a fallback when Wi-Fi geolocation fails.

    Returns:
        dict | None: Dictionary with 'city', 'country', and 'timezone', or None.
    """
    logger.debug("Fetching location fallback using public IP geolocation service...")
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                loc_info = {
                    "city": data.get("city"),
                    "country": data.get("country"),
                    "timezone": data.get("timezone")
                }
                logger.debug(f"IP geolocation fallback succeeded: {loc_info}")
                return loc_info
        logger.warning("IP geolocation fallback service returned unsuccessful status.")
    except requests.RequestException as e:
        logger.error(t('sync_engine_ip_fallback_error').format(e=e))
    return None


def fetch_location_data() -> dict:
    """
    Retrieve location data by trying high-precision Wi-Fi geolocating first, 
    and falling back to IP-based geolocation if Wi-Fi fails.

    Returns:
        dict | None: Dictionary containing 'city', 'country', and 'timezone', or None.
    """
    if has_wifi_hardware():
        logger.info(t('sync_engine_attempting_wifi_geo'))
        coords = fetch_location_from_wifi()

        if coords:
            lat, lng = coords
            city, country = get_city_from_coords(lat, lng)
            if city:
                ip_data = fetch_location_fallback_ip()
                timezone = ip_data.get("timezone") if ip_data else "Europe/Rome"
                
                return {
                    "city": city,
                    "country": country or "Unknown",
                    "timezone": timezone
                }

    logger.warning(t('sync_engine_wifi_geo_fallback'))
    return fetch_location_fallback_ip()


def update_system_timezone(timezone: str) -> None:
    """
    Update the system timezone safely using timedatectl or direct symlink fallback 
    without causing application crashes due to permission blocks.

    Args:
        timezone (str): The valid timezone string to set (e.g., 'Europe/Rome').
    """
    logger.debug(f"Attempting to update system timezone to: {timezone}")
    zone_path = os.path.join("/usr/share/zoneinfo", timezone)
    
    if not os.path.exists(zone_path):
        logger.error(f"Timezone definition file not found on disk: {zone_path}")
        return

    # Method 1: Try via timedatectl command
    try:
        result = subprocess.run(
            ["sudo", "timedatectl", "set-timezone", timezone],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info(f"System timezone successfully updated via timedatectl to: {timezone}")
            return
    except Exception:
        pass

    # Method 2: Fallback via file symlink replacement
    try:
        if os.path.lexists("/etc/localtime"):
            os.unlink("/etc/localtime")
        os.symlink(zone_path, "/etc/localtime")
        
        if os.path.exists("/etc/timezone"):
            with open("/etc/timezone", "w", encoding="utf-8") as f:
                f.write(timezone + "\n")
                
        logger.info(f"System timezone successfully updated via symlink fallback to: {timezone}")
    except Exception as e:
        logger.error(f"Failed to update system timezone due to insufficient permissions or system error: {e}")


def save_location_config(location_info: dict) -> None:
    """
    Save the synchronized location and timezone details to a local JSON configuration file.

    Args:
        location_info (dict): Dictionary containing city, country, and timezone details.
    """
    logger.debug("Saving location and timezone configuration to disk...")
    try:
        data_config = {
            "city": location_info["city"],
            "country": location_info["country"],
            "timezone": location_info["timezone"],
            "last_sync": datetime.datetime.now().isoformat()
        }
        
        # Ensure parent directory exists safely
        os.makedirs(os.path.dirname(config.TIME_PLACE_JSON_CONFIG_PATH), exist_ok=True)
        
        with open(config.TIME_PLACE_JSON_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data_config, f, indent=4, ensure_ascii=False)
            
        logger.debug("Location configuration successfully saved.")
    except Exception as e:
        logger.error(f"Failed to save location configuration file: {e}")


def execute_sync() -> bool:
    """
    Orchestrate the full synchronization process by fetching location data,
    updating the system timezone, and saving the configuration locally.

    Returns:
        bool: True if synchronization succeeded, False otherwise.
    """
    logger.info(t('sync_engine_syncing_time_and_place'))

    location_data = fetch_location_data()
    if not location_data:
        logger.error(t('sync_engine_failed_retrieve_location'))
        return False

    logger.info(t('sync_engine_location_found').format(
        city=location_data['city'], 
        country=location_data['country'], 
        timezone=location_data['timezone']
    ))

    update_system_timezone(location_data["timezone"])
    save_location_config(location_data)

    logger.info(t('sync_engine_synced_successfully'))
    return True


def run_synchronization() -> bool:
    """
    Check for internet connectivity, attempt automatic reconnection if offline,
    and trigger the main time and location synchronization routine.

    Returns:
        bool: True if synchronization completed successfully, False otherwise.
    """
    logger.debug("Starting synchronization workflow...")
    if not check_internet_connection():
        if not try_connection_to_known_networks():
            logger.warning(t('sync_engine_no_internet_available'))
            return False

    return execute_sync()