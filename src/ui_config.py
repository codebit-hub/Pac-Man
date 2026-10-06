import pygame
import os
import math


class UIConfig:
    """Centralized UI settings and common drawing routines."""

    def __init__(self) -> None:
        # Colors
        self.C_BG = (0, 0, 0)
        self.C_BOX_BG = (210,117,206)
        self.C_TEXT_WHITE = (255, 255, 255)
        self.C_TEXT_YELLOW = (255, 255, 0)
        self.C_TEXT_PURPLE = (210, 117, 206)

        self.C_CLOSE_NORMAL = (255, 255, 255)
        self.C_CLOSE_HOVER = (255, 80, 80)

        self.C_GOLD = (255, 215, 0)
        self.C_SILVER = (192, 192, 192)
        self.C_BRONZE = (164,101,40)

        self.GAME_PURPLE = (210, 117, 206)
        self.GAME_PATH = (20, 20, 40)

        # Fonts
        self.font_regular = pygame.font.SysFont(None, 24)
        self.font_title = pygame.font.SysFont(None, 64)
        self.font_title_small = pygame.font.SysFont(None, 36)
        self.font_inst_title = pygame.font.SysFont(None, 24)
        self.font_inst_regular = pygame.font.SysFont(None, 18)
        self.close_font = pygame.font.SysFont(None, 12)
        self.font_hud = pygame.font.SysFont(None, 20)
        self.pause_regular = pygame.font.SysFont(None, 16)

    def draw_panel_bg(self, screen: pygame.Surface,
                      cx: int, cy: int) -> pygame.Rect:
        """Draws the standard cyan UI panel and returns its Rect."""
        panel_w = min(int(screen.get_width() * 0.9), 600)
        panel_h = min(int(screen.get_height() * 0.95), 420)
        bg_rect = pygame.Rect(0, 0, panel_w, panel_h)
        bg_rect.center = (cx, cy)
        from renderer import MLXUtils
        MLXUtils.draw_rect(screen, self.C_BOX_BG, bg_rect)
        return bg_rect

    def draw_close_button(self, screen: pygame.Surface,
                          bg_rect: pygame.Rect) -> pygame.Rect:
        """Draws the 'X' close button at the top-right"""
        mouse_pos = pygame.mouse.get_pos()
        close_margin = 15

        width, height = self.close_font.size("X")

        x = bg_rect.right - close_margin
        y = bg_rect.top + close_margin
        close_rect = pygame.Rect(0, 0, width, height)
        close_rect.topright = (x, y)

        if close_rect.collidepoint(mouse_pos):
            close_color = self.C_CLOSE_HOVER
        else:
            close_color = self.C_CLOSE_NORMAL

        close_surf = self.close_font.render("X", True, close_color)
        screen.blit(close_surf, close_rect)
        return close_rect

    def draw_bullet(self, screen: pygame.Surface, x: int, y: int,
                    color: tuple | None = None,
                    is_centered: bool = False) -> None:
        """Draws a standard triangle bullet point."""
        c = color if color else self.C_TEXT_WHITE
        mid_y = y if is_centered else y + 15
        from renderer import MLXUtils
        MLXUtils.draw_triangle(screen, c, 
            (x - 10, mid_y - 7),
            (x - 10, mid_y + 7),
            (x, mid_y)
        )

    def draw_pulsing_nav(self, screen: pygame.Surface, text: str,
                         cx: int, cy: int) -> None:
        """Draws pulsing text at the given center coordinates."""
        current_time = pygame.time.get_ticks()
        pulse = (math.sin(current_time * 0.005) + 1) / 2
        brightness = int(100 + 155 * pulse)
        color = (brightness, brightness, brightness)
        nav_return = self.font_regular.render(text, True, color)
        screen.blit(nav_return, nav_return.get_rect(center=(cx, cy)))

    def load_icon(self) -> None:
        try:
            pacman_icon = os.path.normpath(os.path.join(
            os.path.dirname(__file__), "..", "assets", "pacman", "pacman-right", "1.png"
            ))
            loaded_img = pygame.image.load(pacman_icon)
            orig_w, orig_h = loaded_img.get_size()
            padded_img = pygame.Surface((orig_w * 2, orig_h * 2), pygame.SRCALPHA)
            padded_img.blit(loaded_img, (orig_w // 2, orig_h // 2))
            pygame.display.set_icon(padded_img)
        except (FileNotFoundError, pygame.error):
            print("Warning: Couldn't load pacman icon")
