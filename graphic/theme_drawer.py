"""
Theme Drawer Module.
Contains specific drawing functions for each UI style/theme, using flat color dictionaries.
"""

import pygame
import math
import random
from graphic.graphic_utils import handle_menu_viewport


def draw_default_menu(screen: pygame.Surface, menu_title: str, menu_options: list, selected_index: int, 
                      menu_subtitle: str, title_font, option_font, colors: dict, button_config: dict, scale_factor: float) -> None:
    
    # Inizializzazione delle variabili di stato persistenti attaccate alla funzione
    if not hasattr(draw_default_menu, "_last_selected"):
        draw_default_menu._last_selected = selected_index
        draw_default_menu._prev_selected = selected_index
        draw_default_menu._anim_start_time = pygame.time.get_ticks()

    current_time = pygame.time.get_ticks()
    animation_duration = 180  # Durata dell'animazione in millisecondi

    # Se cambia la selezione, salviamo la precedente e facciamo ripartire il timer
    if selected_index != draw_default_menu._last_selected:
        draw_default_menu._prev_selected = draw_default_menu._last_selected
        draw_default_menu._last_selected = selected_index
        draw_default_menu._anim_start_time = current_time

    # Calcolo del progresso dell'animazione (0.0 -> 1.0)
    elapsed = current_time - draw_default_menu._anim_start_time
    progress = min(1.0, elapsed / animation_duration)

    screen_width, screen_height = screen.get_size()
    center_x = screen_width // 2

    bg_color = colors.get("background_primary", (20, 20, 20))
    surface_color = colors.get("background_secondary", (50, 50, 50))
    text_color = colors.get("text_primary", (255, 255, 255))
    surface_hover_color = colors.get("hover_fill", (70, 70, 70))
    border_color = colors.get("border_color", (100, 100, 100))
    subtitle_color = colors.get("text_secondary", (150, 150, 150))
    highlight_color = colors.get("highlight_primary", (0, 255, 200))

    screen.fill(bg_color)

    # Disegno barra superiore e titolo
    bar_height = int(50 * scale_factor)
    bar_rect = pygame.Rect(0, int(15 * scale_factor), screen_width, bar_height)
    pygame.draw.rect(screen, surface_color, bar_rect)
    
    border_width = max(1, int(button_config.get("border_width", 2) * scale_factor))
    pygame.draw.line(screen, border_color, (0, bar_rect.top), (screen_width, bar_rect.top), border_width)
    pygame.draw.line(screen, border_color, (0, bar_rect.bottom), (screen_width, bar_rect.bottom), border_width)

    title_surface = title_font.render(menu_title, True, text_color)
    title_rect = title_surface.get_rect(center=(center_x, bar_rect.centery))
    screen.blit(title_surface, title_rect)

    content_start_y = bar_rect.bottom + int(25 * scale_factor)
    current_y = content_start_y
    start_x = int(50 * scale_factor)
    item_spacing = int(50 * scale_factor)

    if menu_subtitle:
        subtitle_surf = option_font.render(menu_subtitle, True, subtitle_color)
        subtitle_rect = subtitle_surf.get_rect(topleft=(start_x, current_y))
        screen.blit(subtitle_surf, subtitle_rect)
        current_y += item_spacing

    line_start_x = start_x
    line_end_x = int(screen_width * (4 / 6))
    max_width = line_end_x - line_start_x

    for i, option_text in enumerate(menu_options):
        row_y = current_y + i * item_spacing
        is_selected = (i == selected_index)
        is_previous = (i == draw_default_menu._prev_selected and draw_default_menu._prev_selected != selected_index)

        current_text_color = surface_hover_color if is_selected else text_color

        text_surf = option_font.render(option_text, True, current_text_color)
        text_rect = text_surf.get_rect(topleft=(start_x, row_y))
        screen.blit(text_surf, text_rect)

        line_y = text_rect.bottom + int(5 * scale_factor)

        # 1. Opzione attualmente selezionata: la barra cresce da sinistra a destra
        if is_selected:
            current_bar_width = int(max_width * progress)
            if current_bar_width > 0:
                bar_surf = pygame.Surface((current_bar_width, max(2, int(2 * scale_factor))), pygame.SRCALPHA)
                for x_offset in range(current_bar_width):
                    # 0% trasparenza a sinistra (alpha 255), più va a destra più è trasparente (alpha diminuisce)
                    alpha = int(255 * (1.0 - (x_offset / max_width)))
                    color_with_alpha = (*highlight_color[:3], alpha)
                    pygame.draw.line(bar_surf, color_with_alpha, (x_offset, 0), (x_offset, bar_surf.get_height() - 1))
                screen.blit(bar_surf, (line_start_x, line_y))

        # 2. Opzione precedente: la barra scompare fluidamente da destra a sinistra
        elif is_previous and progress < 1.0:
            # Usiamo una curva di easing quadratica per rendere il movimento morbidissimo
            smooth_progress = progress * progress
            remaining_width = int(max_width * (1.0 - smooth_progress))
            
            if remaining_width > 0:
                bar_surf = pygame.Surface((remaining_width, max(2, int(2 * scale_factor))), pygame.SRCALPHA)
                for x_offset in range(remaining_width):
                    # Manteniamo la sfumatura coerente: 0% trasparenza a sinistra, trasparente a destra
                    alpha = int(255 * (1.0 - (x_offset / max_width)))
                    alpha = max(0, min(255, alpha))
                    
                    color_with_alpha = (*highlight_color[:3], alpha)
                    pygame.draw.line(bar_surf, color_with_alpha, (x_offset, 0), (x_offset, bar_surf.get_height() - 1))
                
                # Disegniamo la barra fissa a sinistra, lasciando che i pixel a destra vengano tagliati via via
                screen.blit(bar_surf, (line_start_x, line_y))


def draw_abruzzo_menu(screen: pygame.Surface, menu_title: str, menu_options: list, selected_index: int, 
                      menu_subtitle: str, title_font, option_font, colors: dict, button_config: dict, scale_factor: float) -> None:
    
    screen_width, screen_height = screen.get_size()
    center_x = screen_width // 2

    width = int(button_config.get("width", 550) * scale_factor)
    height = int(button_config.get("height", 45) * scale_factor)
    margin_y = int(button_config.get("margin_y", 15) * scale_factor)

    wood_base = (75, 42, 22)
    wood_shadow = (55, 30, 15)
    text_color = (250, 240, 215)
    gold_color = (215, 175, 70)

    screen.fill(wood_base)

    # 1. Tavolo in legno rustico con venature e nodi
    plank_height = int(80 * scale_factor)
    for y_pos in range(0, screen_height + plank_height, plank_height):
        pygame.draw.line(screen, wood_shadow, (0, y_pos), (screen_width, y_pos), max(3, int(4 * scale_factor)))
        for x_offset in range(0, screen_width, 300):
            node_rect = pygame.Rect(x_offset + (y_pos % 130), y_pos + 10, int(40 * scale_factor), int(15 * scale_factor))
            pygame.draw.ellipse(screen, wood_shadow, node_rect, width=int(2 * scale_factor))

    # 2. Rondelle di salame in basso a sinistra (con punti/grasso statici precalcolati)
    salami_cx = int(90 * scale_factor)
    salami_cy = screen_height - int(100 * scale_factor)
    salami_radius = int(38 * scale_factor)
    
    if not hasattr(draw_abruzzo_menu, "_salami_data"):
        draw_abruzzo_menu._salami_data = []
        salami_positions_cfg = [
            (salami_cx, salami_cy, 0),
            (salami_cx + int(32 * scale_factor), salami_cy + int(18 * scale_factor), 22),
            (salami_cx - int(24 * scale_factor), salami_cy + int(28 * scale_factor), -35),
            (salami_cx + int(18 * scale_factor), salami_cy - int(28 * scale_factor), 60)
        ]
        for sx, sy, angle in salami_positions_cfg:
            local_c = salami_radius + 6
            dots = []
            for _ in range(10):
                fx = local_c + random.randint(-int(salami_radius * 0.6), int(salami_radius * 0.6))
                fy = local_c + random.randint(-int(salami_radius * 0.6), int(salami_radius * 0.6))
                dots.append((fx, fy, random.randint(2, 4), random.randint(1, 2)))
            draw_abruzzo_menu._salami_data.append({"sx": sx, "sy": sy, "angle": angle, "dots": dots})

    for item in draw_abruzzo_menu._salami_data:
        s_surf = pygame.Surface((salami_radius * 2 + 12, salami_radius * 2 + 12), pygame.SRCALPHA)
        local_c = salami_radius + 6
        
        pygame.draw.circle(s_surf, (20, 10, 5, 120), (local_c + 3, local_c + 3), salami_radius)
        pygame.draw.circle(s_surf, (235, 225, 210), (local_c, local_c), salami_radius)
        pygame.draw.circle(s_surf, (160, 25, 25), (local_c, local_c), salami_radius - int(5 * scale_factor))
        
        for fx, fy, r1, r2 in item["dots"]:
            pygame.draw.circle(s_surf, (240, 230, 215), (fx, fy), r1 * scale_factor)
            pygame.draw.circle(s_surf, (120, 15, 15), (fx + 1, fy + 1), r2 * scale_factor)

        rotated_salami = pygame.transform.rotate(s_surf, item["angle"])
        screen.blit(rotated_salami, (item["sx"] - rotated_salami.get_width() // 2, item["sy"] - rotated_salami.get_height() // 2))

    # 3. Calice di vino rosso visto dall'alto in alto a destra
    wine_cx = screen_width - int(100 * scale_factor)
    wine_cy = int(100 * scale_factor)
    glass_radius = int(32 * scale_factor)

    glass_surf = pygame.Surface((glass_radius * 2 + 16, glass_radius * 2 + 16), pygame.SRCALPHA)
    gc = glass_radius + 8

    pygame.draw.circle(glass_surf, (20, 10, 5, 100), (gc + 4, gc + 4), glass_radius)
    pygame.draw.circle(glass_surf, (220, 230, 240, 90), (gc, gc), glass_radius, width=int(2 * scale_factor))
    pygame.draw.circle(glass_surf, (100, 12, 20), (gc, gc), glass_radius - int(4 * scale_factor))
    highlight_rect = pygame.Rect(gc - int(12 * scale_factor), gc - int(18 * scale_factor), int(14 * scale_factor), int(6 * scale_factor))
    pygame.draw.ellipse(glass_surf, (255, 255, 255, 70), highlight_rect)

    screen.blit(glass_surf, (wine_cx - gc, wine_cy - gc))

    # --- HEADER ---
    header_w = int(screen_width * 0.7)
    header_h = int(50 * scale_factor)
    header_x = center_x - header_w // 2
    header_y = int(25 * scale_factor)
    
    header_rect = pygame.Rect(header_x, header_y, header_w, header_h)
    pygame.draw.rect(screen, (45, 22, 10), header_rect, border_radius=8)
    pygame.draw.rect(screen, gold_color, header_rect, width=2, border_radius=8)

    title_surf = title_font.render(menu_title, True, gold_color)
    title_rect = title_surf.get_rect(center=header_rect.center)
    screen.blit(title_surf, title_rect)

    current_y = header_y + header_h + int(30 * scale_factor)
    start_x = center_x - width // 2

    if menu_subtitle:
        sub_surf = option_font.render(menu_subtitle, True, text_color)
        screen.blit(sub_surf, (start_x, current_y))
        current_y += int(35 * scale_factor)

    start_index, end_index, visible_options = handle_menu_viewport(
        screen, menu_options, selected_index, current_y, height, margin_y, scale_factor
    )

    selected_bar_rect = None

    # --- OPZIONI MENU ---
    for idx, option_text in enumerate(visible_options):
        actual_index = start_index + idx
        btn_y = current_y + (idx * (height + margin_y))
        
        is_selected = (actual_index == selected_index)
        current_bg = (60, 30, 15) if not is_selected else (115, 38, 16)
        current_border = gold_color if is_selected else (35, 18, 8)
        
        btn_rect = pygame.Rect(start_x, btn_y, width, height)
        
        if is_selected:
            selected_bar_rect = btn_rect

        pygame.draw.rect(screen, current_bg, btn_rect, border_radius=6)
        pygame.draw.rect(screen, current_border, btn_rect, width=2 if is_selected else 1, border_radius=6)

        text_surf = option_font.render(option_text, True, text_color)
        text_rect = text_surf.get_rect(midleft=(start_x + int(20 * scale_factor), btn_y + height // 2))
        screen.blit(text_surf, text_rect)
        
        idx_surf = option_font.render(f"{actual_index + 1}.", True, gold_color if is_selected else text_color)
        idx_rect = idx_surf.get_rect(midright=(start_x + width - int(20 * scale_factor), btn_y + height // 2))
        screen.blit(idx_surf, idx_rect)

    # 4. Taralli che cadono continuamente e si accumulano in fondo allo schermo
    if not hasattr(draw_abruzzo_menu, "_taralli_pool"):
        draw_abruzzo_menu._taralli_pool = []
        draw_abruzzo_menu._spawn_timer = 0

    draw_abruzzo_menu._spawn_timer += 1
    if draw_abruzzo_menu._spawn_timer >= 45 and len(draw_abruzzo_menu._taralli_pool) < 20:
        draw_abruzzo_menu._spawn_timer = 0
        tr_radius = int(15 * scale_factor)
        draw_abruzzo_menu._taralli_pool.append({
            "x": random.randint(start_x + 30, start_x + width - 30),
            "y": -30,
            "speed": random.uniform(2.5, 4.0),
            "radius": tr_radius,
            "resting_y": screen_height - int(30 * scale_factor) - random.randint(0, int(40 * scale_factor)),
            "is_resting": False
        })

    for tarallo in draw_abruzzo_menu._taralli_pool:
        if not tarallo["is_resting"]:
            tarallo["y"] += tarallo["speed"]
            # Controlla se si ferma in fondo allo schermo
            if tarallo["y"] >= tarallo["resting_y"]:
                tarallo["y"] = tarallo["resting_y"]
                tarallo["is_resting"] = True

        tx, ty = int(tarallo["x"]), int(tarallo["y"])
        tr = tarallo["radius"]
        
        tarallo_surf = pygame.Surface((tr * 2 + 10, tr * 2 + 10), pygame.SRCALPHA)
        tc = tr + 5
        
        pygame.draw.circle(tarallo_surf, (20, 10, 5, 100), (tc + 2, tc + 2), tr)
        pygame.draw.circle(tarallo_surf, (215, 170, 115), (tc, tc), tr)
        pygame.draw.circle(tarallo_surf, (130, 85, 45), (tc, tc), tr, width=int(3 * scale_factor))
        pygame.draw.circle(tarallo_surf, wood_base, (tc, tc), int(tr * 0.38))
        pygame.draw.circle(tarallo_surf, (100, 65, 30), (tc, tc), int(tr * 0.38), width=2)
        
        for _ in range(3):
            sx_s = tc + random.randint(-int(tr * 0.5), int(tr * 0.5))
            sy_s = tc + random.randint(-int(tr * 0.5), int(tr * 0.5))
            pygame.draw.circle(tarallo_surf, (255, 255, 255), (sx_s, sy_s), int(1.5 * scale_factor))

        screen.blit(tarallo_surf, (tx - tc, ty - tc))


def draw_pixel_art_menu(screen: pygame.Surface, menu_title: str, menu_options: list, selected_index: int, 
                        menu_subtitle: str, title_font, option_font, colors: dict, button_config: dict, scale_factor: float) -> None:
    screen_width, screen_height = screen.get_size()
    center_x = screen_width // 2

    width = int(button_config.get("width", 500) * scale_factor)
    height = int(button_config.get("height", 45) * scale_factor)
    margin_y = int(button_config.get("margin_y", 15) * scale_factor)
    
    cabinet_bg = colors.get("background_primary", (30, 28, 38))
    screen.fill(cabinet_bg)
    
    def create_pixel_chamfered_surface(bw: int, bh: int, base_col: tuple, shadow_col: tuple, highlight_col: tuple, black_col: tuple) -> pygame.Surface:
        surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        c = 3
        light_edge = (min(255, highlight_col[0]+30), min(255, highlight_col[1]+30), min(255, highlight_col[2]+30))
        
        for y in range(bh):
            for x in range(bw):
                is_top_left = (x < c and y < c and (x + y < c))
                is_top_right = (x >= bw - c and y < c and ((bw - 1 - x) + y < c))
                is_bottom_left = (x < c and y >= bh - c and (x + (bh - 1 - y) < c))
                is_bottom_right = (x >= bw - c and y >= bh - c and ((bw - 1 - x) + (bh - 1 - y) < c))
                
                if is_top_left or is_top_right or is_bottom_left or is_bottom_right:
                    continue
                
                is_top = (y == 0 and c <= x < bw - c)
                is_bottom = (y == bh - 1 and c <= x < bw - c)
                is_left = (x == 0 and c <= y < bh - c)
                is_right = (x == bw - 1 and c <= y < bh - c)
                is_tl_border = (x < c and y < c and (x + y == c))
                is_tr_border = (x >= bw - c and y < c and ((bw - 1 - x) + y == c))
                is_bl_border = (x < c and y >= bh - c and (x + (bh - 1 - y) == c))
                is_br_border = (x >= bw - c and y >= bh - c and ((bw - 1 - x) + (bh - 1 - y) == c))

                if is_top or is_bottom or is_left or is_right or is_tl_border or is_tr_border or is_bl_border or is_br_border:
                    surf.set_at((x, y), (*black_col, 255))
                elif y == 1:
                    surf.set_at((x, y), (*light_edge, 255))
                elif y == 2:
                    surf.set_at((x, y), (*highlight_col, 255))
                elif y >= bh - 4:
                    if y == bh - 4:
                        surf.set_at((x, y), (*shadow_col, 255))
                    elif y == bh - 3 or y == bh - 2:
                        surf.set_at((x, y), (*shadow_col, 255))
                    else:
                        surf.set_at((x, y), (*black_col, 255))
                else:
                    surf.set_at((x, y), (*base_col, 255))
        return surf

    text_color = colors.get("text_primary", (255, 255, 255))
    base_color = colors.get("fill", (53, 143, 60))
    black = colors.get("border_color", (15, 15, 15))

    screen_border_color = colors.get("border_color", (20, 20, 25))
    screen_inner_bg = colors.get("background_secondary", (15, 35, 25))
    
    screen_box_width = int(screen_width * 0.85)
    screen_box_height = int(70 * scale_factor)
    screen_box_rect = pygame.Rect(0, 0, screen_box_width, screen_box_height)
    screen_box_rect.center = (center_x, int(60 * scale_factor))
    
    pygame.draw.rect(screen, screen_border_color, screen_box_rect.inflate(8, 8), border_radius=4)
    pygame.draw.rect(screen, screen_inner_bg, screen_box_rect)
    
    scanline_col = colors.get("background_tertiary", (10, 25, 18))
    for scan_y in range(screen_box_rect.top + 4, screen_box_rect.bottom - 4, int(4 * scale_factor)):
        pygame.draw.line(screen, scanline_col, (screen_box_rect.left + 4, scan_y), (screen_box_rect.right - 4, scan_y))

    title_surf = title_font.render(menu_title, True, colors.get("text_primary", (180, 255, 200)))
    title_rect = title_surf.get_rect(center=screen_box_rect.center)
    screen.blit(title_surf, title_rect)

    current_y = screen_box_rect.bottom + int(30 * scale_factor)
    start_x = int(50 * scale_factor)

    if menu_subtitle:
        subtitle_surf = option_font.render(menu_subtitle, True, colors.get("text_secondary", (200, 200, 200)))
        subtitle_rect = subtitle_surf.get_rect(topleft=(start_x, current_y))
        screen.blit(subtitle_surf, subtitle_rect)
        current_y += int(40 * scale_factor)

    start_index, end_index, visible_options = handle_menu_viewport(
        screen, menu_options, selected_index, current_y, height, margin_y, scale_factor
    )

    for idx, option_text in enumerate(visible_options):
        actual_index = start_index + idx
        btn_y = current_y + (idx * (height + margin_y))
        
        is_selected = (actual_index == selected_index)
        current_base = colors.get("hover_fill", base_color) if is_selected else base_color
        btn_shadow = (max(0, current_base[0]-80), max(0, current_base[1]-80), max(0, current_base[2]-80))
        btn_highlight = (min(255, current_base[0]+60), min(255, current_base[1]+60), min(255, current_base[2]+60))

        btn_base_w, btn_base_h = 140, 28
        raw_btn = create_pixel_chamfered_surface(btn_base_w, btn_base_h, current_base, btn_shadow, btn_highlight, black)
        
        scaled_btn = pygame.transform.scale(raw_btn, (width, height))
        btn_rect = scaled_btn.get_rect(center=(center_x, btn_y + height // 2))
        
        if is_selected:
            btn_rect.y += int(2 * scale_factor)
            cursor_size = int(12 * scale_factor)
            cursor_x_left = btn_rect.left - cursor_size - int(14 * scale_factor)
            cursor_x_right = btn_rect.right + int(14 * scale_factor)
            cursor_y = btn_rect.centery - cursor_size // 2
            
            for cx in [cursor_x_left, cursor_x_right]:
                cursor_rect = pygame.Rect(cx, cursor_y, cursor_size, cursor_size)
                pygame.draw.rect(screen, black, cursor_rect)
                pygame.draw.rect(screen, btn_highlight, cursor_rect.inflate(-2, -2))

        screen.blit(scaled_btn, btn_rect)

        text_surf = option_font.render(option_text, True, text_color)
        text_rect = text_surf.get_rect(center=btn_rect.center)
        if is_selected:
            text_rect.y += int(2 * scale_factor)
            
        screen.blit(text_surf, text_rect)

def draw_hive_menu(screen: pygame.Surface, menu_title: str, menu_options: list, selected_index: int, 
                    menu_subtitle: str, title_font, option_font, colors: dict, button_config: dict, scale_factor: float) -> None:
    
    screen_width, screen_height = screen.get_size()
    center_x = screen_width // 2
    center_y = screen_height // 2

    if not hasattr(draw_hive_menu, "_bees"):
        draw_hive_menu._bees = [
            {
                "x": random.randint(50, screen_width - 50),
                "y": random.randint(50, screen_height - 50),
                "vx": random.choice([-1.2, 1.2]),
                "vy": random.choice([-0.8, 0.8]),
                "wobble": random.random() * 10,
                "change_timer": random.randint(50, 150)
            }
            for _ in range(16)
        ]

    margin_y = int(button_config.get("margin_y", 45) * scale_factor)
    
    core = colors.get("core", colors)
    text_cfg = colors.get("text", colors)
    interactive = colors.get("interactive", {})
    effects = colors.get("effects", colors)

    bg_color = core.get("background_primary", (60, 35, 15))
    hex_base = core.get("background_secondary", bg_color)
    border_color = core.get("border_color", (15, 15, 15))
    
    text_color = text_cfg.get("text_primary", (255, 255, 255))
    title_color = text_cfg.get("text_inverted", text_cfg.get("text_primary", (255, 255, 255)))
    
    default_fill = interactive.get("default", {}).get("fill", colors.get("fill", (245, 200, 40)))
    selected_fill = interactive.get("selected", {}).get("fill", colors.get("hover_fill", (220, 110, 20)))
    
    bee_body_color = effects.get("highlight_primary", default_fill)

    screen.fill(bg_color)
    
    # 1. Sfondo esagonale
    size = int(24 * scale_factor)
    h_dist = size * math.sqrt(3)
    v_dist = size * 1.5
    
    row, y = 0, -size
    while y < screen_height + size:
        col, x_offset = 0, (0 if (row % 2 == 0) else h_dist / 2)
        x = -size + x_offset
        while x < screen_width + h_dist:
            outer_points = [(x + size * math.cos(math.radians(60 * i - 30)), y + size * math.sin(math.radians(60 * i - 30))) for i in range(6)]
            pygame.draw.polygon(screen, hex_base, outer_points)
            pygame.draw.polygon(screen, border_color, outer_points, 1)
            x += h_dist
            col += 1
        y += v_dist
        row += 1

    # 2. Api che gironzolano nello sfondo (ora spawnate in modo più sparso su tutto lo schermo)
    for bee in draw_hive_menu._bees:
        bee["change_timer"] -= 1
        if bee["change_timer"] <= 0:
            bee["vx"] = random.uniform(-1.5, 1.5)
            bee["vy"] = random.uniform(-1.0, 1.0)
            bee["change_timer"] = random.randint(80, 200)

        bee["x"] += bee["vx"]
        bee["y"] += bee["vy"] + math.sin(pygame.time.get_ticks() * 0.005 + bee["wobble"]) * 0.5

        if bee["x"] < 20 or bee["x"] > screen_width - 20:
            bee["vx"] *= -1
        if bee["y"] < 20 or bee["y"] > screen_height - 20:
            bee["vy"] *= -1

        bx, by = bee["x"], bee["y"]
        
        bee_w = int(22 * scale_factor)
        bee_h = int(16 * scale_factor)
        bee_surf = pygame.Surface((bee_w, bee_h), pygame.SRCALPHA)
        
        local_bx = bee_w // 2
        local_by = bee_h // 2

        head_center = (local_bx + int(6 * scale_factor), local_by)
        thorax_rect = pygame.Rect(local_bx + int(1 * scale_factor), local_by - int(4 * scale_factor), int(7 * scale_factor), int(7 * scale_factor))
        abd_rect = pygame.Rect(local_bx - int(7 * scale_factor), local_by - int(5 * scale_factor), int(10 * scale_factor), int(9 * scale_factor))

        pygame.draw.ellipse(bee_surf, bee_body_color, abd_rect)
        pygame.draw.ellipse(bee_surf, border_color, abd_rect, width=1)
        pygame.draw.ellipse(bee_surf, (30, 30, 30), thorax_rect)
        pygame.draw.ellipse(bee_surf, border_color, thorax_rect, width=1)
        pygame.draw.circle(bee_surf, (30, 30, 30), head_center, int(3.5 * scale_factor))

        wing_offset = math.sin(pygame.time.get_ticks() * 0.04 + bee["wobble"]) * int(3 * scale_factor)
        wing_surf = pygame.Surface((int(8 * scale_factor), int(6 * scale_factor)), pygame.SRCALPHA)
        pygame.draw.ellipse(wing_surf, (255, 255, 255, 180), wing_surf.get_rect())
        pygame.draw.ellipse(wing_surf, border_color, wing_surf.get_rect(), width=1)
        
        rotated_wing = pygame.transform.rotate(wing_surf, 20 + wing_offset)
        bee_surf.blit(rotated_wing, (local_bx - int(1 * scale_factor), local_by - int(10 * scale_factor)))

        if bee["vx"] < 0:
            bee_surf = pygame.transform.flip(bee_surf, True, False)

        screen.blit(bee_surf, (bx - bee_w // 2, by - bee_h // 2))

    # 3. Header
    header_width = int(screen_width * 0.75)
    header_height = int(55 * scale_factor)
    header_surf = pygame.Surface((header_width, header_height), pygame.SRCALPHA)
    
    pygame.draw.rect(header_surf, default_fill, header_surf.get_rect(), border_radius=6)
    pygame.draw.rect(header_surf, border_color, header_surf.get_rect(), width=int(3 * scale_factor), border_radius=6)
    header_rect = header_surf.get_rect(center=(center_x, int(50 * scale_factor)))
    screen.blit(header_surf, header_rect)

    title_surf = title_font.render(menu_title, True, title_color)
    screen.blit(title_surf, title_surf.get_rect(center=header_rect.center))

    current_y = header_rect.bottom + int(40 * scale_factor)
    start_x = int(100 * scale_factor)

    if menu_subtitle:
        sub_surf = option_font.render(menu_subtitle, True, text_color)
        screen.blit(sub_surf, sub_surf.get_rect(topleft=(start_x, current_y)))
        current_y += int(50 * scale_factor)

    line_max_width = int(screen_width * 0.6)
    option_height = option_font.get_height()
    item_spacing = max(margin_y, option_height + int(35 * scale_factor))

    # 4. Opzioni menu
    for idx, option_text in enumerate(menu_options):
        row_y = current_y + (idx * item_spacing)
        is_selected = (idx == selected_index)

        current_text_color = selected_fill if is_selected else text_color
        text_surf = option_font.render(option_text, True, current_text_color)
        text_rect = text_surf.get_rect(topleft=(start_x, row_y))
        screen.blit(text_surf, text_rect)

        line_y = text_rect.bottom + int(8 * scale_factor)
        pygame.draw.line(screen, selected_fill if is_selected else border_color, 
                         (start_x, line_y), (start_x + line_max_width, line_y), max(2, int(2 * scale_factor)))

    selected_row_y = current_y + (selected_index * item_spacing)
    box_left = start_x + (line_max_width // 2) + int(15 * scale_factor)
    box_right = start_x + line_max_width - int(5 * scale_factor)
    
    box_top = selected_row_y - int(12 * scale_factor)
    box_bottom = selected_row_y + int(20 * scale_factor)

    if not hasattr(draw_hive_menu, "_guide_bee"):
        draw_hive_menu._guide_bee = {
            "x": float((box_left + box_right) // 2),
            "y": float((box_top + box_bottom) // 2),
            "vx": random.choice([-1.2, 1.2]),
            "vy": random.choice([-0.8, 0.8]),
            "wobble": random.random() * 10,
            "change_timer": random.randint(50, 150)
        }

    guide = draw_hive_menu._guide_bee

    target_center_y = (box_top + box_bottom) / 2.0
    if "current_center_y" not in guide:
        guide["current_center_y"] = target_center_y
    
    guide["current_center_y"] += (target_center_y - guide["current_center_y"]) * 0.04
    current_height_offset = (box_bottom - box_top) / 2.0
    
    dynamic_box_top = guide["current_center_y"] - current_height_offset
    dynamic_box_bottom = guide["current_center_y"] + current_height_offset

    guide["change_timer"] -= 1
    if guide["change_timer"] <= 0:
        guide["vx"] = random.uniform(-1.5, 1.5)
        guide["vy"] = random.uniform(-1.0, 1.0)
        guide["change_timer"] = random.randint(80, 200)

    guide["x"] += guide["vx"]
    guide["y"] += guide["vy"] + math.sin(pygame.time.get_ticks() * 0.005 + guide["wobble"]) * 0.5

    if guide["x"] <= box_left:
        guide["x"] = box_left
        guide["vx"] *= -1
    elif guide["x"] >= box_right:
        guide["x"] = box_right
        guide["vx"] *= -1

    if guide["y"] <= dynamic_box_top:
        guide["y"] = dynamic_box_top
        guide["vy"] *= -1
    elif guide["y"] >= dynamic_box_bottom:
        guide["y"] = dynamic_box_bottom
        guide["vy"] *= -1

    bx, by = guide["x"], guide["y"]

    # Disegno dell'Ape Regina (regolata con corona e addome allungato)
    bee_w = int(26 * scale_factor)
    bee_h = int(18 * scale_factor)
    guide_surf = pygame.Surface((bee_w, bee_h), pygame.SRCALPHA)
    
    local_bx = bee_w // 2
    local_by = bee_h // 2

    head_center = (local_bx + int(7 * scale_factor), local_by)
    thorax_rect = pygame.Rect(local_bx + int(1 * scale_factor), local_by - int(4 * scale_factor), int(7 * scale_factor), int(7 * scale_factor))
    abd_rect = pygame.Rect(local_bx - int(9 * scale_factor), local_by - int(5 * scale_factor), int(13 * scale_factor), int(9 * scale_factor))

    pygame.draw.ellipse(guide_surf, bee_body_color, abd_rect)
    pygame.draw.ellipse(guide_surf, border_color, abd_rect, width=1)
    pygame.draw.ellipse(guide_surf, (30, 30, 30), thorax_rect)
    pygame.draw.ellipse(guide_surf, border_color, thorax_rect, width=1)
    pygame.draw.circle(guide_surf, (30, 30, 30), head_center, int(3.5 * scale_factor))

    crown_color = (255, 215, 0)
    hx, hy = head_center[0], head_center[1] - int(4 * scale_factor)
    crown_points = [
        (hx - int(3 * scale_factor), hy),
        (hx - int(3 * scale_factor), hy - int(3 * scale_factor)),
        (hx - int(1 * scale_factor), hy - int(1 * scale_factor)),
        (hx, hy - int(4 * scale_factor)),
        (hx + int(1 * scale_factor), hy - int(1 * scale_factor)),
        (hx + int(3 * scale_factor), hy - int(3 * scale_factor)),
        (hx + int(3 * scale_factor), hy)
    ]
    pygame.draw.polygon(guide_surf, crown_color, crown_points)
    pygame.draw.polygon(guide_surf, border_color, crown_points, width=1)

    wing_offset = math.sin(pygame.time.get_ticks() * 0.04 + guide["wobble"]) * int(3 * scale_factor)
    wing_surf = pygame.Surface((int(9 * scale_factor), int(6 * scale_factor)), pygame.SRCALPHA)
    pygame.draw.ellipse(wing_surf, (255, 255, 255, 180), wing_surf.get_rect())
    pygame.draw.ellipse(wing_surf, border_color, wing_surf.get_rect(), width=1)
    
    rotated_wing = pygame.transform.rotate(wing_surf, 20 + wing_offset)
    guide_surf.blit(rotated_wing, (local_bx - int(1 * scale_factor), local_by - int(11 * scale_factor)))

    if guide["vx"] < 0:
        guide_surf = pygame.transform.flip(guide_surf, True, False)

    screen.blit(guide_surf, (int(bx - bee_w // 2), int(by - bee_h // 2)))
    
def draw_blueprint_menu(screen: pygame.Surface, menu_title: str, menu_options: list, selected_index: int, 
                        menu_subtitle: str, title_font, option_font, colors: dict, button_config: dict, scale_factor: float) -> None:
    screen_width, screen_height = screen.get_size()
    center_x = screen_width // 2

    width = int(button_config.get("width", 540) * scale_factor)
    height = int(button_config.get("height", 45) * scale_factor)
    margin_y = int(button_config.get("margin_y", 18) * scale_factor)
    
    bg_color = colors.get("background_primary", (15, 35, 75))
    surface_color = colors.get("fill", (20, 50, 105))
    hover_color = colors.get("hover_fill", (35, 75, 140))
    border_color = colors.get("border_color", (180, 210, 255))
    text_color = colors.get("text_primary", (240, 245, 255))
    dim_color = colors.get("background_tertiary", (90, 130, 190))

    screen.fill(bg_color)
    
    grid_fine_color = colors.get("background_secondary", (22, 45, 90))
    fine_grid = int(15 * scale_factor)
    for x in range(0, screen_width, fine_grid):
        pygame.draw.line(screen, grid_fine_color, (x, 0), (x, screen_height), 1)
    for y in range(0, screen_height, fine_grid):
        pygame.draw.line(screen, grid_fine_color, (0, y), (screen_width, y), 1)

    major_grid = int(75 * scale_factor)
    for x in range(0, screen_width, major_grid):
        pygame.draw.line(screen, dim_color, (x, 0), (x, screen_height), 1)
    for y in range(0, screen_height, major_grid):
        pygame.draw.line(screen, dim_color, (0, y), (screen_width, y), 1)

    def create_cad_box_surface(bw: int, bh: int, fill_col: tuple, border_col: tuple, is_selected: bool) -> pygame.Surface:
        surf = pygame.Surface((bw + 50, bh + 30), pygame.SRCALPHA)
        box_rect = pygame.Rect(25, 15, bw, bh)
        
        pygame.draw.rect(surf, fill_col, box_rect)
        
        border_w = int(2 * scale_factor) if not is_selected else int(3 * scale_factor)
        pygame.draw.rect(surf, border_col, box_rect, width=border_w)
        
        marker_len = int(8 * scale_factor)
        pygame.draw.line(surf, border_col, (box_rect.left, box_rect.top - 4), (box_rect.left + marker_len, box_rect.top - 4), 1)
        pygame.draw.line(surf, border_col, (box_rect.left - 4, box_rect.top), (box_rect.left - 4, box_rect.top + marker_len), 1)
        pygame.draw.line(surf, border_col, (box_rect.right - marker_len, box_rect.bottom + 4), (box_rect.right, box_rect.bottom + 4), 1)
        pygame.draw.line(surf, border_col, (box_rect.right + 4, box_rect.bottom - marker_len), (box_rect.right + 4, box_rect.bottom), 1)

        selection_marker_color = colors.get("text_inverted", (255, 255, 100))
        if is_selected:
            pygame.draw.rect(surf, selection_marker_color, box_rect, width=2)
            pygame.draw.circle(surf, selection_marker_color, (box_rect.left, box_rect.centery), int(3 * scale_factor))
            pygame.draw.circle(surf, selection_marker_color, (box_rect.right, box_rect.centery), int(3 * scale_factor))
        else:
            inner_rect = pygame.Rect(box_rect.x + 6, box_rect.y + 6, box_rect.width - 12, box_rect.height - 12)
            inner_border_color = colors.get("background_secondary", (60, 110, 170))
            pygame.draw.rect(surf, inner_border_color, inner_rect, width=1)

        return surf

    header_width = int(screen_width * 0.75)
    header_height = int(55 * scale_factor)
    header_surf = create_cad_box_surface(header_width, header_height, surface_color, border_color, False)
    header_rect = header_surf.get_rect(center=(center_x, int(50 * scale_factor)))
    
    screen.blit(header_surf, header_rect)

    title_surf = title_font.render(menu_title, True, text_color)
    title_rect = title_surf.get_rect(center=header_rect.center)
    screen.blit(title_surf, title_rect)

    current_y = header_rect.bottom + int(30 * scale_factor)
    start_x = int(60 * scale_factor)

    if menu_subtitle:
        subtitle_color = colors.get("text_secondary", (180, 210, 255))
        subtitle_surf = option_font.render(menu_subtitle, True, subtitle_color)
        subtitle_rect = subtitle_surf.get_rect(topleft=(start_x, current_y))
        screen.blit(subtitle_surf, subtitle_rect)
        current_y += int(40 * scale_factor)

    start_index, end_index, visible_options = handle_menu_viewport(
        screen, menu_options, selected_index, current_y, height, margin_y, scale_factor
    )

    for idx, option_text in enumerate(visible_options):
        actual_index = start_index + idx
        btn_y = current_y + (idx * (height + margin_y))
        is_selected = (actual_index == selected_index)

        current_fill = hover_color if is_selected else surface_color
        selection_marker_color = colors.get("text_inverted", (255, 255, 100))
        current_border = selection_marker_color if is_selected else border_color
        
        raw_btn = create_cad_box_surface(width, height, current_fill, current_border, is_selected)
        btn_rect = raw_btn.get_rect(center=(center_x, btn_y + height // 2))

        screen.blit(raw_btn, btn_rect)

        selection_text_color = colors.get("text_inverted", (255, 255, 150))
        current_text_color = selection_text_color if is_selected else text_color
        text_surf = option_font.render(option_text, True, current_text_color)
        text_rect = text_surf.get_rect(center=btn_rect.center)
        
        screen.blit(text_surf, text_rect)


def draw_glitch_menu(screen: pygame.Surface, menu_title: str, menu_options: list, selected_index: int, 
                     menu_subtitle: str, title_font, option_font, colors: dict, button_config: dict, scale_factor: float) -> None:
    screen_width, screen_height = screen.get_size()
    center_x = screen_width // 2

    bg_color = colors.get("background_primary", (20, 20, 20))
    screen.fill(bg_color)
    
    if random.random() < 0.3:
        noise_surf = pygame.Surface((screen_width, screen_height))
        noise_surf.fill((0, 0, 0))
        for _ in range(1000):
            nx = random.randint(0, screen_width)
            ny = random.randint(0, screen_height)
            noise_color = random.randint(0, 30)
            noise_surf.set_at((nx, ny), (noise_color, noise_color, noise_color))
        noise_surf.set_alpha(20)
        screen.blit(noise_surf, (0, 0))

    col_green = colors.get("highlight_primary", (50, 255, 50))
    col_red = colors.get("glitch_primary", (255, 50, 50))
    col_blue = colors.get("glitch_secondary", (50, 50, 255))

    def draw_chromatic_text(text_to_draw, font_obj, color_obj, pos_center, x_offset_glitch=0, y_offset_glitch=0):
        x_base, y_base = pos_center
        ch_dist = max(1, int(2 * scale_factor)) 
        
        s_r = font_obj.render(text_to_draw, True, col_red)
        s_r.set_alpha(150)
        screen.blit(s_r, s_r.get_rect(center=(x_base - ch_dist + x_offset_glitch, y_base + ch_dist / 2 + y_offset_glitch)))

        s_b = font_obj.render(text_to_draw, True, col_blue)
        s_b.set_alpha(150)
        screen.blit(s_b, s_b.get_rect(center=(x_base + ch_dist + x_offset_glitch, y_base - ch_dist / 2 + y_offset_glitch)))

        s_g = font_obj.render(text_to_draw, True, color_obj)
        screen.blit(s_g, s_g.get_rect(center=(x_base + x_offset_glitch, y_base + y_offset_glitch)))

    start_y_title = int(45 * scale_factor)
    # Il titolo usa title_font per risultare più grande e in evidenza
    draw_chromatic_text(menu_title, title_font, col_green, (center_x, start_y_title))

    content_start_y = start_y_title + int(70 * scale_factor)
    item_spacing = int(55 * scale_factor)

    current_y = content_start_y
    if menu_subtitle:
        sub_surf = option_font.render(menu_subtitle, True, col_green)
        sub_rect = sub_surf.get_rect(center=(center_x, current_y))
        screen.blit(sub_surf, sub_rect)
        current_y += item_spacing

    start_index, end_index, visible_options = handle_menu_viewport(
        screen, menu_options, selected_index, current_y, item_spacing, 0, scale_factor
    )

    for idx, option_text in enumerate(visible_options):
        actual_index = start_index + idx
        row_y = current_y + (idx * item_spacing)
        is_selected = (actual_index == selected_index)

        if is_selected:
            display_text = f"<< {option_text} >>"
            glitch_active = random.random() < 0.15
            
            g_ox = random.randint(-10, 10) if glitch_active else 0
            g_oy = random.randint(-4, 4) if glitch_active else 0
            
            curr_opt_color = col_green
            if glitch_active and random.random() < 0.3:
                curr_opt_color = bg_color
                tmp_r = option_font.render(display_text, True, curr_opt_color)
                tmp_rect = tmp_r.get_rect(center=(center_x + g_ox, row_y + g_oy))
                bar_rect = tmp_rect.inflate(int(20 * scale_factor), int(4 * scale_factor))
                pygame.draw.rect(screen, col_green, bar_rect)

            # Le opzioni usano option_font (più piccolo del titolo)
            draw_chromatic_text(display_text, option_font, curr_opt_color, (center_x, row_y), g_ox, g_oy)
            
            if glitch_active and random.random() < 0.5:
                if random.random() < 0.5:
                    lx1 = center_x - int(random.randint(100, 200) * scale_factor)
                    lx2 = center_x + int(random.randint(100, 200) * scale_factor)
                    ly = row_y + int(random.randint(-15, 15) * scale_factor)
                    line_color = col_red if random.random() < 0.5 else col_blue
                    pygame.draw.line(screen, line_color, (lx1, ly), (lx2, ly), random.randint(1, 3))
                else:
                    rx = center_x + int(random.randint(-150, 150) * scale_factor)
                    rw = int(random.randint(5, 15) * scale_factor)
                    rh = int(random.randint(2, 6) * scale_factor)
                    ry = row_y + int(random.randint(-10, 10) * scale_factor)
                    pygame.draw.rect(screen, col_green, (rx, ry, rw, rh))
        else:
            display_text = f"[ {option_text} ]"
            draw_chromatic_text(display_text, option_font, col_green, (center_x, row_y))

    scanline_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    for l_y in range(0, screen_height, 3):
        pygame.draw.line(scanline_surf, (0, 0, 0, 80), (0, l_y), (screen_width, l_y), 1)
    screen.blit(scanline_surf, (0, 0))

    vignette_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    pygame.draw.ellipse(vignette_surf, (0, 0, 0, 180), (0, int(-screen_height / 2), screen_width, int(screen_height * 2)))
    pygame.draw.ellipse(vignette_surf, (0, 0, 0, 255), (int(-screen_width / 2), 0, int(screen_width * 2), screen_height))
    
    inv_vignette = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    inv_vignette.fill((0, 0, 0))
    inv_vignette.blit(vignette_surf, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
    screen.blit(inv_vignette, (0, 0))
    
    pygame.draw.rect(screen, (0, 0, 0), screen.get_rect(), int(10 * scale_factor))


DRAWER_CATALOG = {
    "default": draw_default_menu,
    "abruzzo": draw_abruzzo_menu,
    "pixel_art": draw_pixel_art_menu,
    "hive": draw_hive_menu,
    "blueprint": draw_blueprint_menu,
    "glitch": draw_glitch_menu
}