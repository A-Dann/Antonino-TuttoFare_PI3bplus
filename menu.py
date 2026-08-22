#!/usr/bin/env python3
import sys

import pygame
from graphic.menu_renderer import render_menu
from menu_modules import desktop_mode, turn_off, dual_audio
import settings
from graphic.display import init_display
from utils.i18n import t

def main():
    screen = init_display()
    clock = pygame.time.Clock()

    menu_options=[t('menu_desktop_mode'),
                  t('menu_dual_audio'),
                  t('menu_settings'),
                  t('menu_exit')
    ]

    selected_index = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                turn_off.run()
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_options)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:  # Tasto INVIO
                    if selected_index == 0:
                        desktop_mode.run()
                    elif selected_index == 1:
                        dual_audio.run()
                    elif selected_index == 2:
                        settings.run()
                    elif selected_index == 3:
                        turn_off.run()
                        running = False
                elif event.key == pygame.K_ESCAPE:
                    turn_off.run()
                    running = False

        # 2. Disegno del menu grafico tramite il renderer
        render_menu(
            screen=screen,
            menu_title=t('menu_title'),
            menu_options=menu_options,
            selected_index=selected_index
        )

        # 3. Aggiornamento dello schermo
        pygame.display.flip()

        # 4. Limitazione a 60 FPS
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()