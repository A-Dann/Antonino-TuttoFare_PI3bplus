#!/usr/bin/env python3
"""
Desktop Mode Engine

This module provides utility functions to retrieve system statistics (CPU, memory,
disk, uptime, temperature) as well as current date, time, timezone, location data, 
and outdoor temperature loaded from a local configuration file and weather API. 
It checks for the presence of the configuration file at startup, attempts synchronization 
if missing, fetches outdoor temperature hourly while updating and clearing the screen 
completely every 5 seconds, and runs in a continuous loop until a key is pressed.
"""

import time
import psutil
import datetime
import json
import os
import sys
import select
import termios
import tty
import requests
import config
import settings_modules.sync_time_and_place as sync_time_and_place
from utils.i18n import t

# Global variables to cache outdoor temperature, track last fetch time, and track last success
cached_outdoor_temp = "N/A"
last_outdoor_temp_fetch = 0
last_successful_fetch = 0

def fetch_outdoor_temperature() -> str:
    global cached_outdoor_temp, last_outdoor_temp_fetch, last_successful_fetch
    
    current_time = time.time()
    
    if last_successful_fetch > 0 and (current_time - last_successful_fetch > 3600):
        return t('desktop_mode_connection_lost')

    if current_time - last_outdoor_temp_fetch < 3600 and cached_outdoor_temp != "N/A":
        return cached_outdoor_temp

    last_outdoor_temp_fetch = current_time

    try:
        ip_response = requests.get("http://ip-api.com/json/", timeout=5)
        ip_data = ip_response.json()
        
        if ip_data.get("status") == "success":
            lat = ip_data.get("lat")
            lon = ip_data.get("lon")
            
            if lat and lon:
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m"
                weather_response = requests.get(weather_url, timeout=5)
                weather_data = weather_response.json()
                
                temp = weather_data.get("current", {}).get("temperature_2m")
                if temp is not None:
                    cached_outdoor_temp = f"{temp:.1f}°C"
                    last_successful_fetch = current_time
                    return cached_outdoor_temp
    except Exception:
        pass

    if last_successful_fetch > 0 and (current_time - last_successful_fetch <= 3600):
        return cached_outdoor_temp

    return t('reconnect_wifi')

def get_info() -> dict:
    now = datetime.datetime.now()
    current_date = now.strftime("%d-%m-%Y")
    current_time_zone = time.tzname[time.daylight]
    current_time = now.strftime("%H:%M:%S")

    city = t('unknown_city')
    country = ""
    if os.path.exists(config.TIME_PLACE_JSON_CONFIG_PATH):
        try:
            with open(config.TIME_PLACE_JSON_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                city = data.get("city", t('unknown_city'))
                country = data.get("country", "")
        except Exception:
            pass

    outdoor_temp = fetch_outdoor_temperature()

    return {
        t('key_date'): current_date,
        t('key_time'): current_time,
        t('key_timezone'): current_time_zone,
        t('key_city'): city,
        t('key_country'): country,
        t('key_outdoor_temperature'): outdoor_temp
    }

def get_stats() -> dict:
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    disk = psutil.disk_usage('/')
    disk_percent = disk.percent
    
    uptime_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds()
    uptime_string = str(datetime.timedelta(seconds=int(uptime_seconds)))

    cpu_temp = "N/A"
    temp_path = "/sys/class/thermal/thermal_zone0/temp"
    if os.path.exists(temp_path):
        try:
            with open(temp_path, "r") as f:
                raw_temp = int(f.read().strip())
                cpu_temp = f"{raw_temp / 1000.0:.1f}°C"
        except Exception:
            pass

    return {
        t('key_cpu_usage'): f"{cpu_percent}%",
        t('key_memory_usage'): f"{memory_percent}%",
        t('key_disk_usage'): f"{disk_percent}%",
        t('key_uptime'): uptime_string,
        t('key_cpu_temperature'): cpu_temp
    }

def ensure_synchronized() -> bool:
    if os.path.exists(config.TIME_PLACE_JSON_CONFIG_PATH):
        return True

    print(t('desktop_mode_config_not_found'))
    success = sync_time_and_place.run()

    if not success or not os.path.exists(config.TIME_PLACE_JSON_CONFIG_PATH):
        print(t('desktop_mode_init_failed'))
        print(t('desktop_mode_cannot_start'))
        return False

    return True

def is_key_pressed() -> bool:
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    return bool(dr)

def run():
    print(t('desktop_mode_starting'))

    if not ensure_synchronized():
        return

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setcbreak(fd)
        time.sleep(1)
        
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print(t('desktop_mode_header'))
            print(t('desktop_mode_label_info'))
            print(json.dumps(get_info(), indent=4, ensure_ascii=False))
            print(t('desktop_mode_label_stats'))
            print(json.dumps(get_stats(), indent=4, ensure_ascii=False))
            print(t('desktop_mode_any_key_to_exit'))

            start_time = time.time()
            while time.time() - start_time < 5:
                if is_key_pressed():
                    sys.stdin.read(1)
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print(t('desktop_mode_exiting'))
                    return
                time.sleep(0.1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    run()