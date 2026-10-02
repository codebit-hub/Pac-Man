from typing_extensions import NoExtraItems
import pygame
import os
import math

class UIConfig:
    """Centralized UI settings and common drawing routines."""
    
    def __init__(self) -> None:
        # Colors
        self.C_BG = (0, 0, 0)
        self.C_BOX_BG = (70, 191, 238)  # Pacman blue
        self.C_TEXT_WHITE = (255, 255, 255)
        self.C_TEXT_YELLOW = (255, 255, 0)
        self.C_TEXT_CYAN = (70, 191, 238)
        
        self.C_CLOSE_NORMAL = (255, 255, 255)
        self.C_CLOSE_HOVER = (255, 80, 80)
        
        self.C_GOLD = (255, 215, 0)
        self.C_SILVER = (192, 192, 192)
        self.C_BRONZE = (205, 127, 50)

        # Fonts
        try:
            _font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "main-font", "Emulogic-zrEw.ttf")
            self.font_regular = pygame.font.Font(os.path.normpath(_font_path), 16)
            self.font_title = pygame.font.Font(os.path.normpath(_font_path), 48)
            self.font_title_small = pygame.font.Font(os.path.normpath(_font_path), 26)
            self.font_inst_title = pygame.font.Font(os.path.normpath(_font_path), 16)
            self.font_inst_regular = pygame.font.Font(os.path.normpath(_font_path), 12)
        except (pygame.error, FileNotFoundError):
            print("Warning: Custom font missing. Using default.")
            self.font_regular = pygame.font.SysFont(None, 24)
            self.font_title = pygame.font.SysFont(None, 64)
            self.font_title_small = pygame.font.SysFont(None, 36)
            self.font_inst_title = pygame.font.SysFont(None, 24)
            self.font_inst_regular = pygame.font.SysFont(None, 18)

    def draw_panel_bg(self, screen: pygame.Surface, cx: int, cy: int, w_ratio: float = 0.9, h_ratio: float = 0.95, max_w: int = 600, max_h: int = 420) -> pygame.Rect:
        """Draws the standard cyan UI panel and returns its Rect."""
        panel_w = min(int(screen.get_width() * w_ratio), max_w)
        panel_h = min(int(screen.get_height() * h_ratio), max_h)
        bg_rect = pygame.Rect(0, 0, panel_w, panel_h)
        bg_rect.center = (cx, cy)
        pygame.draw.rect(screen, self.C_BOX_BG, bg_rect)
        return bg_rect

    def draw_close_button(self, screen: pygame.Surface, bg_rect: pygame.Rect) -> pygame.Rect:
        """Draws the 'X' close button at the top-right of the bg_rect and returns its Rect for collision detection."""
        mouse_pos = pygame.mouse.get_pos()
        close_margin = 15
        dummy_surf = self.font_inst_title.render("X", True, self.C_TEXT_WHITE)
        close_rect = dummy_surf.get_rect(topright=(bg_rect.right - close_margin, bg_rect.top + close_margin))
        close_color = self.C_CLOSE_HOVER if close_rect.collidepoint(mouse_pos) else self.C_CLOSE_NORMAL
        close_surf = self.font_inst_title.render("X", True, close_color)
        screen.blit(close_surf, close_rect)
        return close_rect

    def draw_bullet(self, screen: pygame.Surface, x: int, y: int, color: tuple = None, is_centered: bool = False) -> None:
        """Draws a standard triangle bullet point."""
        c = color if color else self.C_TEXT_WHITE
        mid_y = y if is_centered else y + 15
        pygame.draw.polygon(screen, c, [
            (x - 10, mid_y - 7),
            (x - 10, mid_y + 7),
            (x, mid_y),
        ])

    def draw_pulsing_nav(self, screen: pygame.Surface, text: str, cx: int, cy: int, font: pygame.font.Font = None) -> None:
        """Draws pulsing text (e.g. 'PRESS ESC TO RETURN') at the given center coordinates."""
        current_time = pygame.time.get_ticks()
        pulse = (math.sin(current_time * 0.005) + 1) / 2
        alpha = int(100 + 155 * pulse)
        f = font if font else self.font_regular
        nav_return = f.render(text, True, self.C_TEXT_WHITE)
        nav_return.set_alpha(alpha)
        screen.blit(nav_return, nav_return.get_rect(center=(cx, cy)))
