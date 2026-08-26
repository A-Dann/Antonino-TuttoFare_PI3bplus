#!/usr/bin/env python3
"""
Wi-Fi Captive Portal Engine

Flask web server running locally when AP mode is active.
It serves the password request page and saves the submitted credentials.
"""

import os
import time
import socket
import threading
from flask import Flask, render_template, request

from antonino_tuttofare.config import TEMP_SELECTED_WIFI_INFO_JSON_PATH, TEMPLATES_DIR_PATH
from antonino_tuttofare.utility.files_utils import read_json, write_json
from antonino_tuttofare.utility.i18n import t, current_lang
from antonino_tuttofare.utility.logger import get_logger

logger = get_logger(__name__)

app = Flask(__name__, template_folder=str(TEMPLATES_DIR_PATH))


def run_captive_dns() -> None:
    """
    Listens on UDP port 53 and responds to ALL DNS queries 
    with the Raspberry Pi local IP (10.42.0.1) to trigger captive portal detection.
    """
    local_ip = "10.42.0.1"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(("0.0.0.0", 53))
        logger.info("Captive DNS server started successfully on port 53.")
    except Exception as e:
        logger.error(f"Failed to bind captive DNS server on port 53: {e}")
        return

    while True:
        try:
            data, addr = sock.recvfrom(512)
            if len(data) < 12:
                continue
            
            transaction_id = data[:2]
            flags = b'\x81\x80'  # Standard response, no error
            qdcount = data[4:6]
            ancount = b'\x00\x01'  # 1 answer
            nscount = b'\x00\x00'
            arcount = b'\x00\x00'
            
            idx = 12
            while idx < len(data) and data[idx] != 0:
                idx += data[idx] + 1
            idx += 5  # Skip null byte and QTYPE/QCLASS
            question = data[12:idx]
            
            answer = b'\xc0\x0c'  # Pointer to domain name
            answer += b'\x00\x01'  # Type A (IPv4)
            answer += b'\x00\x01'  # Class IN
            answer += b'\x00\x00\x00\x3c'  # TTL (60 seconds)
            answer += b'\x00\x04'  # Data length (4 bytes)
            answer += socket.inet_aton(local_ip)
            
            response = transaction_id + flags + qdcount + ancount + nscount + arcount + question + answer
            sock.sendto(response, addr)
        except Exception:
            break


def shutdown_server() -> None:
    """Stops the Flask server cleanly."""
    logger.debug("Initiating server shutdown sequence...")
    try:
        func = request.environ.get('werkzeug.server.shutdown')
        if func is not None:
            func()
            logger.info("Flask server shut down via Werkzeug environment handler.")
        else:
            logger.warning("Werkzeug shutdown handler not found. Forcing process exit.")
            os._exit(0)
    except Exception as e:
        logger.error(f"Error during server shutdown: {e}")
        os._exit(0)


def delayed_shutdown(delay: int = 5) -> None:
    """Executes server shutdown after a specified delay."""
    logger.debug(f"Scheduling server shutdown in {delay} seconds...")
    time.sleep(delay)
    shutdown_server()


@app.route('/')
def index() -> str:
    """Displays the password request page for the selected network."""
    logger.debug("Serving captive portal index page...")
    try:
        data = read_json(TEMP_SELECTED_WIFI_INFO_JSON_PATH) or {}
        ssid = data.get("ssid", "Wi-Fi")
    except Exception as e:
        logger.error(f"Failed to read temporary Wi-Fi info file: {e}")
        ssid = "Wi-Fi"
    
    return render_template(
        'wifi_portal_password_request.html',
        selected_ssid=ssid,
        t=t,
        current_lang=current_lang
    )


@app.route('/connect', methods=['POST'])
def connect() -> str:
    """Receives the password, saves it, renders the received page, and triggers a delayed shutdown."""
    logger.info("Received connection credentials submission from captive portal.")
    try:
        password = request.form.get('password', '')
        
        data = read_json(TEMP_SELECTED_WIFI_INFO_JSON_PATH) or {}
        ssid = data.get("ssid", "Wi-Fi")

        data["password"] = password
        write_json(TEMP_SELECTED_WIFI_INFO_JSON_PATH, data)
        logger.debug(f"Credentials successfully saved for SSID: '{ssid}'")

        threading.Thread(target=delayed_shutdown, args=(5,)).start()
    except Exception as e:
        logger.error(f"Failed to process and save submitted Wi-Fi credentials: {e}")

    return render_template(
        'wifi_portal_password_received.html',
        ssid=ssid if 'ssid' in locals() else "Wi-Fi",
        t=t,
        current_lang=current_lang
    )


@app.route('/generate_204')
@app.route('/gen_204')
def android_captive() -> str:
    """Redirect for Android captive portal checks."""
    logger.debug("Intercepted Android captive portal check request.")
    return index()


@app.route('/hotspot-detect.html')
def apple_captive() -> str:
    """Redirect for Apple/iOS captive portal checks."""
    logger.debug("Intercepted Apple captive portal check request.")
    return index()


@app.route('/connecttest.txt')
@app.route('/ncsi.txt')
def windows_captive() -> str:
    """Redirect for Windows captive portal checks."""
    logger.debug("Intercepted Windows captive portal check request.")
    return index()


@app.route('/<path:text>', methods=['GET', 'POST'])
def catch_all(text: str) -> str:
    """Catches all other requests and redirects them to the captive portal index."""
    logger.debug(f"Intercepted wildcard/catch-all request for path: '{text}'")
    return index()


if __name__ == '__main__':
    # Start the captive DNS server in a background daemon thread
    dns_thread = threading.Thread(target=run_captive_dns, daemon=True)
    dns_thread.start()

    logger.info("Starting Wi-Fi Captive Portal web server on port 80...")
    app.run(host='0.0.0.0', port=80)