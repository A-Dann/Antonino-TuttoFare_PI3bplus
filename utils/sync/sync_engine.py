#!/usr/bin/env python3
"""
Sync Engine Module

This module handles network connectivity checks, automatic reconnection via NetworkManager,
high-precision Wi-Fi geolocation using the Mozilla Location Service, reverse geocoding via OpenStreetMap,
IP-based location as fallback, system timezone updates, and local configuration persistence.
"""

import json
import datetime
import subprocess
import time
import config
import requests
from utils.i18n import t


def check_internet_connection():
    """
    Check for internet connectivity by pinging Google.

    Returns:
        bool: True if internet is reachable (HTTP 200), False otherwise.
    """
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def try_connection_to_known_networks():
    """
    Attempt automatic reconnection to known Wi-Fi networks using NetworkManager.

    Returns:
        bool: True if connection is successfully established, False otherwise.
    """
    print(t('sync_engine_currently_offline'))

    subprocess.run(["nmcli", "networking", "on"])
    time.sleep(5)

    return check_internet_connection()

def has_wifi_hardware():
    """
    Check if the system has a functional Wi-Fi interface for high-precision scanning.

    Returns:
        bool: True if a Wi-Fi device is present, False otherwise.
    """
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "TYPE", "dev"],
            capture_output=True,
            text=True,
            check=True
        )
        return "wifi" in result.stdout.lower()
    except Exception:
        return False

def scan_wifi_networks():
    """
    Scan nearby Wi-Fi networks and extract their MAC addresses and signal strengths.

    Returns:
        list[dict]: A list of dictionaries containing 'macAddress' and 'signalStrength'.
    """
    if not has_wifi_hardware():
        return []

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
        return networks
    except Exception as e:
        print(t('sync_engine_wifi_scan_error').format(e=e))
        return []

def fetch_location_from_wifi():
    """
    Use Mozilla Location Service (MLS) via nearby Wi-Fi networks to get precise coordinates.

    Returns:
        tuple[float, float] | None: A tuple containing (latitude, longitude), or None if it fails.
    """
    wifi_list = scan_wifi_networks()
    if not wifi_list:
        return None

    url = "https://location.services.mozilla.com/v1/geolocate?key=test"
    payload = {"wifiAccessPoints": wifi_list}
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()

            lat = data.get("location", {}).get("lat")
            lng = data.get("location", {}).get("lng")

            if lat and lng:
                return lat, lng
            
    except requests.RequestException as e:
        print(t('sync_engine_mozilla_geo_error').format(e=e))
    
    return None

def get_city_from_coords(lat, lng):
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
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})

            city = address.get("city") or address.get("town") or address.get("village") or address.get("municipality")
            country = address.get("country")

            return city, country
        
    except requests.RequestException as e:
        print(t('sync_engine_nominatim_error').format(e=e))
    
    return None, None

def fetch_location_fallback_ip():
    """
    Retrieve location data based on public IP as a fallback when Wi-Fi geolocation fails.

    Returns:
        dict | None: Dictionary with 'city', 'country', and 'timezone', or None.
    """
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()

        if data.get("status") == "success":
            return {
                "city": data.get("city"),
                "country": data.get("country"),
                "timezone": data.get("timezone")
            }
        
    except requests.RequestException as e:
        print(t('sync_engine_ip_fallback_error').format(e=e))
    return None

def fetch_location_data():
    """
    Retrieve location data by trying high-precision Wi-Fi geolocating first, 
    and falling back to IP-based geolocation if Wi-Fi fails.

    Returns:
        dict | None: Dictionary containing 'city', 'country', and 'timezone', or None.
    """
    if has_wifi_hardware():
        print(t('sync_engine_attempting_wifi_geo'))
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

    print(t('sync_engine_wifi_geo_fallback'))
    return fetch_location_fallback_ip()

def update_system_timezone(timezone):
    """
    Update the system timezone using the Linux timedatectl utility.

    Args:
        timezone (str): The valid timezone string to set (e.g., 'Europe/Rome').
    """
    subprocess.run(["sudo", "timedatectl", "set-timezone", timezone])

def save_location_config(location_info):
    """
    Save the synchronized location and timezone details to a local JSON configuration file.

    Args:
        location_info (dict): Dictionary containing city, country, and timezone details.
    """
    data_config = {
        "city": location_info["city"],
        "country": location_info["country"],
        "timezone": location_info["timezone"],
        "last_sync": datetime.datetime.now().isoformat()
    }
    with open(config.TIME_PLACE_JSON_CONFIG_PATH, "w") as f:
        json.dump(data_config, f, indent=4)

def execute_sync():
    """
    Orchestrate the full synchronization process by fetching location data,
    updating the system timezone, and saving the configuration locally.

    Returns:
        bool: True if synchronization succeeded, False otherwise.
    """
    print(t('sync_engine_syncing_time_and_place'))

    location_data = fetch_location_data()
    if not location_data:
        print(t('sync_engine_failed_retrieve_location'))
        return False

    print(t('sync_engine_location_found').format(
        city=location_data['city'], 
        country=location_data['country'], 
        timezone=location_data['timezone']
    ))

    update_system_timezone(location_data["timezone"])
    save_location_config(location_data)

    print(t('sync_engine_synced_successfully'))
    return True

def run_synchronization():
    """
    Check for internet connectivity, attempt automatic reconnection if offline,
    and trigger the main time and location synchronization routine.

    Returns:
        bool: True if synchronization completed successfully, False otherwise.
    """
    if not check_internet_connection():
        if not try_connection_to_known_networks():
            print(t('sync_engine_no_internet_available'))
            return False

    return execute_sync()