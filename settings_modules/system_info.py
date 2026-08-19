#!/usr/bin/env python3
"""
System Info Module

This module retrieves and displays detailed system information about the Raspberry Pi,
such as OS version, kernel, hostname, IP address, and hardware temperatures.
"""

import platform
import subprocess
import psutil
import os
from utils.i18n import t

def get_system_details() -> dict:
    hostname = platform.node()
    os_name = platform.system()
    os_release = platform.release()
    processor = platform.processor() or t('unknown_processor')

    # Tries to retrieve the IP address of the Raspberry Pi
    ip_address = "N/A"
    try:
        s = psutil.net_if_addrs()
        for interface, addrs in s.items():
            if interface != 'lo':
                for addr in addrs:
                    if addr.family == 2:  # AF_INET (IPv4)
                        ip_address = addr.address
                        break
                if ip_address != "N/A":
                    break
    except Exception:
        pass

    # Tries to retrieve the CPU temperature
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
        t('sys_hostname'): hostname,
        t('sys_os'): f"{os_name} {os_release}",
        t('sys_ip_address'): ip_address,
        t('sys_processor'): processor,
        t('sys_cpu_temperature'): cpu_temp
    }

def run():
    print(t('msg_fetching_sys_info'))

    os.system('clear' if os.name == 'posix' else 'cls')
    print(t('msg_system_info_title'))
    
    details = get_system_details()
    for key, value in details.items():
        print(f"{key}: {value}")
        
    print("\n-------------------------")
    input(t('msg_press_enter_return'))

if __name__ == "__main__":
    run()