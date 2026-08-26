#!/usr/bin/env python3
"""
Wi-Fi Captive Portal Engine

Flask web server running locally when AP mode is active.
It serves the password request page and saves the submitted credentials.
"""

import os
import time
import threading
from flask import Flask, render_template, request
from src.antonino_tuttofare.config import TEMP_SELECTED_WIFI_INFO_JSON_PATH
from antonino_tuttofare.utility.files_utils import read_json, write_json
from src.antonino_tuttofare.utility.i18n import t, current_lang


app = Flask(__name__)

def shutdown_server():
    """Stops the Flask server cleanly."""
    func = request.environ.get('werkzeug.server.shutdown')
    if func is not None:
        func()
    else:
        os._exit(0)

def delayed_shutdown(delay=5):
    """Executes server shutdown after a 5-second delay."""
    time.sleep(delay)
    shutdown_server()

@app.route('/')
def index():
    """Displays the password request page for the selected network."""
    data = read_json(TEMP_SELECTED_WIFI_INFO_JSON_PATH)
    ssid = data.get("ssid", "Wi-Fi")
    
    return render_template(
        'wifi_portal_password_request.html',
        selected_ssid=ssid,
        t=t,
        current_lang=current_lang
    )

@app.route('/connect', methods=['POST'])
def connect():
    """Receives the password, saves it, renders the received page, and triggers a delayed shutdown."""
    password = request.form.get('password')
    
    data = read_json(TEMP_SELECTED_WIFI_INFO_JSON_PATH)
    ssid = data.get("ssid", "Wi-Fi")

    data["password"] = password
    write_json(TEMP_SELECTED_WIFI_INFO_JSON_PATH, data)

    threading.Thread(target=delayed_shutdown, args=(5,)).start()

    return render_template(
        'wifi_portal_password_received.html',
        ssid=ssid,
        t=t,
        current_lang=current_lang
    )

@app.route('/generate_204')
@app.route('/gen_204')
def android_captive():
    """Redirect per Android captive portal check"""
    return index()

@app.route('/hotspot-detect.html')
def apple_captive():
    """Redirect per Apple/iOS captive portal check"""
    return index()

@app.route('/connecttest.txt')
@app.route('/ncsi.txt')
def windows_captive():
    """Redirect per Windows captive portal check"""
    return index()

@app.route('/<path:text>', methods=['GET', 'POST'])
def catch_all(text):
    """Catches all other requests and redirects them to the captive portal index."""
    return index()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)