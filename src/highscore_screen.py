import pygame
import sys
from typing import Any
from ui_config import UIConfig

from highscore import HighScoreManager


class Highscorescreen:
    """Manages and renders the highscore leaderboard screen."""

    def __init__(self, screen: pygame.Surface,
                 highscores: HighScoreManager) -> None:
        """Initialize Highscorescreen with a display surface"""

        self.screen = screen
        self.highscores = highscores
        self.ui = UIConfig()

    def _run_highscore_screen(self, app: Any) -> None:
        """Draw Highscore leaderboard."""
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif (ev.type == pygame.KEYDOWN
                  or ev.type == pygame.MOUSEBUTTONDOWN):
                app.app_state = "MENU"

        self.screen.fill((0, 0, 0))
        bg_rect = self.ui.draw_panel_bg(self.screen, cx, cy)

        # X button
        self.ui.draw_close_button(self.screen, bg_rect)

        c = self.ui.C_TEXT_WHITE
        title = self.ui.font_regular.render("TOP 10 SCORES", True, c)
        self.screen.blit(title, title.get_rect(center=(cx, bg_rect.top + 20)))

        start_y = bg_rect.top + 95
        step_y = max(20, (bg_rect.height - 110) // 10)

        for i, hs in enumerate(self.highscores.scores):
            if i == 0:
                color = self.ui.C_GOLD
            elif i == 1:
                color = self.ui.C_SILVER
            elif i == 2:
                color = self.ui.C_BRONZE
            else:
                color = self.ui.C_TEXT_WHITE

            # Left align name
            txt = f"{i+1}. {hs['name']}"
            name_txt = self.ui.font_regular.render(txt, True, color)
            pos = (bg_rect.left + 40, start_y + (i * step_y))
            name_rect = name_txt.get_rect(midleft=pos)
            self.screen.blit(name_txt, name_rect)

            # Right align score
            txt = f"{hs['score']}"
            score_txt = self.ui.font_regular.render(txt, True, color)
            pos = (bg_rect.right - 40, start_y + (i * step_y))
            score_rect = score_txt.get_rect(midright=pos)
            self.screen.blit(score_txt, score_rect)

        try:
            img_path = "./assets/others/return-instuctions.png"
            ret_img = pygame.image.load(img_path)
            rect = ret_img.get_rect(center=(cx, bg_rect.bottom + 50))
            self.screen.blit(ret_img, rect)
        except (FileNotFoundError, pygame.error):
            pass
        pygame.display.flip()
