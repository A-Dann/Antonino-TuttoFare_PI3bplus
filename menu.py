#!/usr/bin/env python3
from menu_modules import desktop_mode, turn_off
from menu_modules import dual_audio
import settings

def main():
    while True:
        print("\n--- MULTITOOL PI ---")
        print("1. Desktop Mode")
        print("2. Dual Audio")
        print("3. Settings")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            print("Switching to Desktop Mode...")
            desktop_mode.run()
        elif choice == '2':
            print("Starting Dual Audio application...")
            dual_audio.run()
        elif choice == '3':
            print("Opening Settings...")
            settings.run()
        elif choice == '4':
            print("Exiting...")
            turn_off.run()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()