import pygame
import sys
from utils.i18n import t

def show_message_screen(screen, message_lines):
    """
    Displays a fullscreen informational screen with a list of text lines
    and waits for the user to press a key (Enter, Escape, or Space) to go back.
    """
    clock = pygame.time.Clock()
    
    # Initialize fonts
    font = pygame.font.SysFont(None, 28)
    title_font = pygame.font.SysFont(None, 36)
    
    screen_width, screen_height = screen.get_size()
    center_x = screen_width // 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE):
                    return

        # Fill background with dark tone
        screen.fill((20, 20, 20))

        # Calculate vertical starting position to center the text block
        total_lines = len(message_lines) + 1  # +1 for the footer
        block_height = total_lines * 40
        start_y = (screen_height - block_height) // 2

        # Render message lines
        current_y = start_y
        for i, line in enumerate(message_lines):
            # Highlight the first line as a title/main status if needed
            f = title_font if i == 0 else font
            text_surf = f.render(str(line), True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(center_x, current_y))
            screen.blit(text_surf, text_rect)
            current_y += 45

        # Render footer instruction ("Press any key to continue")
        footer_surf = font.render(t('msg_press_enter_to_continue'), True, (150, 150, 150))
        footer_rect = footer_surf.get_rect(center=(center_x, screen_height - 60))
        screen.blit(footer_surf, footer_rect)

        pygame.display.flip()
        clock.tick(60)