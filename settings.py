import sys
from settings_modules import system_info
import settings_modules.sync_time_and_place as sync_time_and_place

def show_system_info():
    print("Fetching system information...")
    system_info.run()

def connect_to_wifi():
    print("Connect to Wi-Fi feature is not implemented yet.")
    return

def start_syncronization():
    success = sync_time_and_place.run()
    if(success):
        print("Time and place synchronized successfully.")
    else:
        print("Failed to synchronize time and place.")
    return

def change_language():
    print("Change Language feature is not implemented yet.")
    return

def back_to_menu():
    print("Returning to the main menu...")
    return

def run():
    while True:
        print("\n--- SETTINGS ---")
        print("1. System Info")
        print("2. Connect to Wi-fi")
        print("3. Sync Time & Place")
        print("4. Change Language")
        print("5. Back to Menu")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == '1':
            show_system_info()
        elif choice == '2':
            connect_to_wifi()
        elif choice == '3':
            start_syncronization()
        elif choice == '4':
            change_language()
        elif choice == '5':
            back_to_menu()
            break
        else:
            print("Invalid choice. Please try again.")