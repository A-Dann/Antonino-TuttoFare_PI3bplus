#!/usr/bin/env python3
import pygame
import graphic.display as display
import menu, settings
from settings_modules import configure_wifi, change_theme, change_language

def main():
    screen, virtual_screen = display.init_display()
    clock = pygame.time.Clock()

    current_state = "MAIN_MENU"
    selected_index = 0
    
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                current_state = "EXIT"

        previous_state = current_state

        if current_state == "MAIN_MENU":
            current_state, selected_index = menu.draw_frame(virtual_screen, selected_index, events)      
        elif current_state == "SETTINGS":
            current_state, selected_index = settings.draw_frame(virtual_screen, selected_index, events)
        elif current_state == "CONFIGURE_WIFI":
            current_state, selected_index = configure_wifi.draw_frame(virtual_screen, selected_index, events)
        elif current_state == "CHANGE_THEME":
            current_state, selected_index = change_theme.draw_frame(virtual_screen, selected_index, events)
        elif current_state == "CHANGE_LANGUAGE":
            current_state, selected_index = change_language.draw_frame(virtual_screen, selected_index, events)
        elif current_state == "EXIT":
            running = False

        if current_state != previous_state:
            selected_index = 0

        display.update_display(screen, virtual_screen)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()