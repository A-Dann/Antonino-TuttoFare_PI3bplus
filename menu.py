#!/usr/bin/env python3
import subprocess
import sys
import config

def desktop_mode():
    print("Switching to Desktop Mode...")
    subprocess.run([sys.executable, config.DESKTOP_MODE_PATH])

def app_bluetooth_dual_audio():
    print("Starting Dual Audio application...")
    subprocess.run([sys.executable, config.DUAL_AUDIO_PATH])

def settings():
    print("Opening Settings...")
    subprocess.run([sys.executable, config.SETTINGS_PATH])

def turn_off():
    subprocess.run([sys.executable, config.TURN_OFF_PATH])
    sys.exit(0)

def main():
    while True:
        print("\n--- MULTITOOL PI ---")
        print("1. Desktop Mode")
        print("2. Dual Audio")
        print("3. Settings")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            desktop_mode()
        elif choice == '2':
            app_bluetooth_dual_audio()
        elif choice == '3':
            settings()
        elif choice == '4':
            turn_off()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()