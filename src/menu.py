import math
from re import S
from re import A
import pygame
import sys
import os
from renderer import Render
from ui_config import UIConfig

class Menu:
    def __init__(self, screen: pygame.Surface, pacgums_power: int = 10, super_pacgums_power: int = 50, pacgums_nb: int = 4) -> None:
        self.screen = screen
        self.state = "main"
        self.pacgums_power = pacgums_power
        self.super_pacgums_power = super_pacgums_power
        self.pacgums_nb = pacgums_nb
        self.selected_item = 0
        self._menu_rects: list[pygame.Rect] = []
        self.anime_x: int = 1000
        self.ui = UIConfig()

        self.renderer = Render()
        main_spritesheet = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets", "spritesheets", "main-spritesheet.png"))
        self.renderer.load_spritesheet(main_spritesheet)

        self.last_anim_time = pygame.time.get_ticks()
        self.anim_frame = 0

        self.pacman_frames = []
        pacman_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets", "pacman", "pacman-left"))
        for i in range(1, 4):
            path = os.path.join(pacman_dir, f"{i}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                self.pacman_frames.append(pygame.transform.scale(img, (28, 28)))
            except Exception:
                pass

    def draw_main_menu(self, top_scores: list = None) -> None:
        self.screen.fill((0, 0, 0))

        # Helper function for getting assets (used by both states)
        def get_sp(x: int, y: int):
            surf = self.renderer.get_sprite(x, y)
            if surf:
                scaled = pygame.transform.scale(surf, (28, 28))
                scaled.set_colorkey((255, 0, 255))
                return scaled
            return pygame.Surface((28, 28))

        # Animation logic (used by main state)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_anim_time >= 100:
            self.last_anim_time = current_time
            self.anim_frame = (self.anim_frame + 1) % 3

        if self.pacman_frames:
            pacman = self.pacman_frames[self.anim_frame % len(self.pacman_frames)]
        else:
            pacman = get_sp(1, 0)

        blinky = get_sp(0, 8)
        pinky = get_sp(2, 8)
        inky = get_sp(4, 8)
        clyde = get_sp(6, 8)

        if self.state == "main":
            NORMAL_COLOR  = (255, 255, 255)
            SELECTED_COLOR = (70,191,238)
            EXIT_COLOR = (208, 62, 25)

            labels = [
                "View Highscores",
                "Instructions",
                "Exit"
            ]

            cx = self.screen.get_width() // 2
            cy = self.screen.get_height() // 2

            # 1. Draw Title
            title = self.ui.font_title.render("Pac-Man", True, (253, 255, 0))
            self.screen.blit(title, title.get_rect(center=(cx - 20, cy - 200)))
            self.ui.draw_pulsing_nav(self.screen, "Push SPACE for play", cx - 5, cy - 100, font=self.ui.font_regular)


            # 2. Draw Menu Items & Pointer
            self._menu_rects = []
            for i, label in enumerate(labels):
                if i == 2 and i == self.selected_item:
                    color = self.ui.C_CLOSE_HOVER
                elif i == self.selected_item:
                    color = self.ui.C_TEXT_CYAN
                else:
                    color = self.ui.C_TEXT_WHITE

                surf = self.ui.font_regular.render(label, True, color)
                rect = surf.get_rect(center=(cx, cy - 30 + (i * 45)))
                self._menu_rects.append(rect)
                self.screen.blit(surf, rect)

                if i == self.selected_item:
                    self.ui.draw_bullet(self.screen, rect.left - 15, rect.centery, color=color, is_centered=True)

            # 3. Draw Top 4 Highscores
            if top_scores:
                hs_title = self.ui.font_regular.render("Top Scores", True, (253, 255, 0))
                self.screen.blit(hs_title, hs_title.get_rect(center=(cx, cy + 120)))
                for idx, hs in enumerate(top_scores):
                    text = f"{idx + 1}. {hs['name']} - {hs['score']} PTS"
                    surf = self.ui.font_regular.render(text, True, (255, 255, 255))
                    self.screen.blit(surf, surf.get_rect(center=(cx, cy + 155 + (idx * 25))))

            # 4. Draw Animation
            start_x = cx - 90
            y_pos = cy + 280

            if self.anime_x > start_x:
                self.anime_x -= 8
            else:
                self.anime_x = start_x

            # Draw only once per frame at the current position
            pygame.draw.circle(self.screen, (255,255,255), [self.anime_x, y_pos + 15], 5)
            pygame.draw.circle(self.screen, (255,255,255), [self.anime_x + 38, y_pos + 15], 5)
            self.screen.blit(pacman, (self.anime_x + 76, y_pos))
            self.screen.blit(clyde, (self.anime_x + 114, y_pos))
            self.screen.blit(blinky, (self.anime_x + 152, y_pos))
            self.screen.blit(pinky, (self.anime_x + 190, y_pos))
            self.screen.blit(inky, (self.anime_x + 228, y_pos))

            self._instruction_rect = self._menu_rects[2]

        elif self.state == "instructions":
            cx = self.screen.get_width() // 2
            cy = self.screen.get_height() // 2

            # --- Panel ---
            bg_rect = self.ui.draw_panel_bg(self.screen, cx, cy)

            ins_title = self.ui.font_inst_title.render("Instructions", True, self.ui.C_TEXT_WHITE)
            blink_ghost_white = get_sp(10, 4)
            pacman_txt = self.ui.font_inst_regular.render("avoids", True, self.ui.C_TEXT_WHITE)
            self.screen.blit(ins_title, ins_title.get_rect(center=(cx, bg_rect.top + 30)))

            self._close_rect = self.ui.draw_close_button(self.screen, bg_rect)


            y_pos = bg_rect.top + 70
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            self.screen.blit(pacman, pacman.get_rect(topleft=(bg_rect.left + 30, y_pos)))
            txt_rect = pacman_txt.get_rect(topleft=(bg_rect.left + 70, y_pos + 5))
            self.screen.blit(pacman_txt, txt_rect)
            ghost_x = txt_rect.right + 10
            self.screen.blit(blinky, blinky.get_rect(topleft=(ghost_x, y_pos)))
            self.screen.blit(pinky, pinky.get_rect(topleft=(ghost_x + 30, y_pos)))
            self.screen.blit(inky, inky.get_rect(topleft=(ghost_x + 60, y_pos)))
            self.screen.blit(clyde, clyde.get_rect(topleft=(ghost_x + 90, y_pos)))

            y_pos = bg_rect.top + 120
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            dots_txt = self.ui.font_inst_regular.render(f"PACGUMS SCORE {self.pacgums_power} POINTS", True, self.ui.C_TEXT_WHITE)
            pygame.draw.circle(self.screen, self.ui.C_TEXT_WHITE, [bg_rect.left + 35, y_pos + 15], 5)
            pygame.draw.circle(self.screen, self.ui.C_TEXT_WHITE, [bg_rect.left + 50, y_pos + 15], 5)
            pygame.draw.circle(self.screen, self.ui.C_TEXT_WHITE, [bg_rect.left + 65, y_pos + 15], 5)
            self.screen.blit(dots_txt, dots_txt.get_rect(topleft=(bg_rect.left + 85, y_pos + 5)))

            y_pos = bg_rect.top + 170
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            pacgums_nb_txt = self.ui.font_inst_regular.render(f"{self.pacgums_nb}", True, self.ui.C_TEXT_WHITE)
            pacgums_power_txt = self.ui.font_inst_regular.render(f"FLASHING SUPER PACGUMS SCORE {self.super_pacgums_power} POINTS", True, self.ui.C_TEXT_WHITE)
            self.screen.blit(pacgums_nb_txt, pacgums_nb_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 5)))
            pygame.draw.circle(self.screen, self.ui.C_TEXT_WHITE, [bg_rect.left + 65, y_pos + 12], 10)
            self.screen.blit(pacgums_power_txt, pacgums_power_txt.get_rect(topleft=(bg_rect.left + 90, y_pos + 5)))

            y_pos = bg_rect.top + 220
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            energezing_pc_txt = self.ui.font_inst_regular.render("AFTER POWER UP", True, self.ui.C_TEXT_WHITE)
            energezing_ghost_txt = self.ui.font_inst_regular.render("CAN EAT", True, self.ui.C_TEXT_WHITE)
            self.screen.blit(energezing_pc_txt, energezing_pc_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 5)))
            self.screen.blit(pacman, pacman.get_rect(topleft=(bg_rect.left + 220, y_pos)))
            self.screen.blit(energezing_ghost_txt, energezing_ghost_txt.get_rect(topleft=(bg_rect.left + 260, y_pos + 5)))
            self.screen.blit(blink_ghost_white, blink_ghost_white.get_rect(topleft=(bg_rect.left + 360, y_pos)))

            y_pos = bg_rect.top + 270
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            controls_txt = self.ui.font_inst_regular.render("CONTROLS: [W][A][S][D] OR ARROWS TO MOVE", True, self.ui.C_TEXT_WHITE)
            self.screen.blit(controls_txt, controls_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 5)))

            # Added Pause Instructions
            y_pos = bg_rect.top + 310
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            pause_txt = self.ui.font_inst_regular.render("PAUSE: PRESS [P] OR [SPACE]", True, self.ui.C_TEXT_WHITE)
            self.screen.blit(pause_txt, pause_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 5)))

            # Pulsing ESC hint
            self.ui.draw_pulsing_nav(self.screen, "PRESS [ESC] TO RETURN OR CLICK", cx, bg_rect.bottom + 20)



    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard and mouse input for menu navigation."""
        NUM_ITEMS = 3

        if self.state == "main":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_item = (self.selected_item + 1) % NUM_ITEMS
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_item = (self.selected_item - 1) % NUM_ITEMS
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self._activate_item(self.selected_item + 1)
                elif event.key == pygame.K_SPACE:
                    self._activate_item(0)
                elif event.key == pygame.K_1:
                    self._activate_item(1)
                elif event.key == pygame.K_2:
                    self._activate_item(2)
                elif event.key == pygame.K_3:
                    self._activate_item(3)
            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(self._menu_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_item = i
                        break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self._menu_rects):
                    if rect.collidepoint(event.pos):
                        self._activate_item(i + 1)
                        break

        elif self.state == "instructions":
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                self.state = "main"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hasattr(self, "_close_rect") and self._close_rect.collidepoint(event.pos):
                    self.state = "main"
                else:
                    self.state = "main"

    def _activate_item(self, index: int) -> None:
        """Execute the action for the selected menu item."""
        if index == 2:
            self.state = "instructions"
        elif index == 3:
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 800))
    pygame.display.set_caption("Menu Test")

    menu = Menu(screen)
    menu.state = "main"

    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            menu.handle_event(event)

        menu.draw_main_menu()
        pygame.display.flip()
        clock.tick(60)
