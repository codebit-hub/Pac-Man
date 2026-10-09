import pygame


class UIConfig:
    """Centralized UI settings and common drawing routines."""

    def __init__(self) -> None:
        """Sets up colors, fonts"""

        # Colors
        self.C_BG = (0, 0, 0)
        self.C_BOX_BG = (210, 117, 206)
        self.C_TEXT_WHITE = (255, 255, 255)
        self.C_TEXT_YELLOW = (255, 255, 0)
        self.C_TEXT_PURPLE = (210, 117, 206)

        self.C_CLOSE_NORMAL = (255, 255, 255)
        self.C_CLOSE_HOVER = (255, 80, 80)

        self.C_GOLD = (255, 215, 0)
        self.C_SILVER = (192, 192, 192)
        self.C_BRONZE = (164, 101, 40)

        self.GAME_PURPLE = (210, 117, 206)
        self.GAME_PATH = (20, 20, 40)

        # Font
        self.font_regular = pygame.font.SysFont(None, 20)

    def draw_panel_bg(self, screen: pygame.Surface,
                      cx: int, cy: int) -> pygame.Rect:
        """Draws the standard cyan UI panel and returns its Rect."""

        bg_rect = pygame.Rect(0, 0, 600, 420)
        bg_rect.center = (cx, cy)
        from renderer import MLXUtils
        MLXUtils.draw_rect(screen, self.C_BOX_BG, bg_rect)
        return bg_rect

    def draw_bullet(self, screen: pygame.Surface, x: int, y: int) -> None:
        """Draws a standard triangle bullet point."""

        c = self.C_TEXT_WHITE
        mid_y = y + 15
        from renderer import MLXUtils
        MLXUtils.draw_triangle(
            screen, c,
            (x - 10, mid_y - 7),
            (x - 10, mid_y + 7),
            (x, mid_y)
        )

    def draw_close_button(self, screen: pygame.Surface,
                          bg_rect: pygame.Rect) -> pygame.Rect:
        """Draws the 'X' close button at the top-right"""

        mouse_pos = pygame.mouse.get_pos()
        close_margin = 20

        width, height = self.font_regular.size("X")

        x = bg_rect.right - close_margin
        y = bg_rect.top + close_margin
        close_rect = pygame.Rect(0, 0, width, height)
        close_rect.topright = (x, y)

        if close_rect.collidepoint(mouse_pos):
            close_color = self.C_CLOSE_HOVER
        else:
            close_color = self.C_CLOSE_NORMAL

        close_surf = self.font_regular.render("X", True, close_color)
        screen.blit(close_surf, close_rect)
        return close_rect
