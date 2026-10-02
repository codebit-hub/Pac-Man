import pygame
import sys
from ui_config import UIConfig

class Highscorescreen:
    def __init__(self, screen: pygame.Surface, highscores) -> None:
        self.screen = screen
        self.highscores = highscores
        self.ui = UIConfig()
    
    def _run_highscore_screen(self, app) -> None:
        """Draw Highscore leaderboard."""
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.VIDEORESIZE:
                app.render.resize(ev.w, ev.h)
            elif ev.type == pygame.KEYDOWN or ev.type == pygame.MOUSEBUTTONDOWN:
                app.app_state = "MENU"

        self.screen.fill((0, 0, 0))
        bg_rect = self.ui.draw_panel_bg(self.screen, cx, cy)
        
        # X button
        self.ui.draw_close_button(self.screen, bg_rect)
        
        title = self.ui.font_title_small.render("TOP 10 SCORES", True, self.ui.C_TEXT_WHITE)
        self.screen.blit(title, title.get_rect(center=(cx, bg_rect.top + 40)))

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

            # Left align name (with rank)
            name_txt = self.ui.font_regular.render(f"{i+1}. {hs['name']}", True, color)
            name_rect = name_txt.get_rect(midleft=(bg_rect.left + 40, start_y + (i * step_y)))
            self.screen.blit(name_txt, name_rect)
            
            # Right align score
            score_txt = self.ui.font_regular.render(f"{hs['score']}", True, color)
            score_rect = score_txt.get_rect(midright=(bg_rect.right - 40, start_y + (i * step_y)))
            self.screen.blit(score_txt, score_rect)

        # Pulsing text
        self.ui.draw_pulsing_nav(self.screen, "PRESS [ESC] TO RETURN OR CLICK", cx, bg_rect.bottom - 20)

        pygame.display.flip()
