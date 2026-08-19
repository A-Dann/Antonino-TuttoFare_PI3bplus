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

def get_system_details() -> dict:
    hostname = platform.node()
    os_name = platform.system()
    os_release = platform.release()
    processor = platform.processor() or "Unknown"
    
    # Recupera l'indirizzo IP locale se connesso
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

    # Temperatura CPU
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
        "Hostname": hostname,
        "OS": f"{os_name} {os_release}",
        "IP Address": ip_address,
        "Processor": processor,
        "CPU Temperature": cpu_temp
    }

def run():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("=== SYSTEM INFORMATION ===")
    
    details = get_system_details()
    for key, value in details.items():
        print(f"{key}: {value}")
        
    print("\n-------------------------")
    input("Press Enter to return to settings...")

if __name__ == "__main__":
    run()