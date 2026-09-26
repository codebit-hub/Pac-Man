from pygame import font
import pygame
import sys
import os
from renderer import Render

class Menu:
    def __init__(self, screen: pygame.Surface, dot_power: int = 10, pacgum_power: int = 50, pacgums_nb: int = 4) -> None:
        self.screen = screen
        self.state = "main"
        self.dot_power = dot_power
        self.pacgum_power = pacgum_power
        self.pacgums_nb = pacgums_nb
        self.selected_item = 0
        self._menu_rects: list[pygame.Rect] = []

        self.renderer = Render()
        spritesheet_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "Sprites", "2-Sprites", "spritesheet.png"))
        self.renderer.load_spritesheet(spritesheet_path)

        try:
            _font_path = os.path.join(os.path.dirname(__file__), "..", "emulogic-font", "Emulogic-zrEw.ttf")
            self.font_regular = pygame.font.Font(os.path.normpath(_font_path), 16)
            self.font_title = pygame.font.Font(os.path.normpath(_font_path), 48)
            self.font_inst_title = pygame.font.Font(os.path.normpath(_font_path), 16)
            self.font_inst_regular = pygame.font.Font(os.path.normpath(_font_path), 12)
        except (pygame.error, FileNotFoundError) as err:
            print("Warning: Custom font missing. Using default.")
            self.font = pygame.font.SysFont(None, 36)

    def draw_main_menu(self) -> None:
        self.screen.fill((0,0,0))
        if self.state == "main":
            NORMAL_COLOR  = (255, 255, 255)
            SELECTED_COLOR = (70,191,238)

            labels = ["1. Start Game", "2. Instructions", "3. HighScores", "4. Exit"]

            cx = self.screen.get_width() // 2
            cy = self.screen.get_height() // 2

            title = self.font_title.render("Pac-Man", True, (253, 255, 0))
            self.screen.blit(title, title.get_rect(center=(cx, cy - 100)))

            self._menu_rects = []
            for i, label in enumerate(labels):
                color = SELECTED_COLOR if i == self.selected_item else NORMAL_COLOR
                surf = self.font_regular.render(label, True, color)
                rect = surf.get_rect(center=(cx, cy + i * 50))
                self._menu_rects.append(rect)
                self.screen.blit(surf, rect)

            # Keep _instruction_rect for backward compat
            self._instruction_rect = self._menu_rects[1]

        elif self.state == "instructions":
            cx = self.screen.get_width() // 2
            cy = self.screen.get_height() // 2

            # --- Panel ---
            panel_w, panel_h = 550, 500
            bg_rect = pygame.Rect(0, 0, panel_w, panel_h)
            bg_rect.center = (cx, cy)
            pygame.draw.rect(self.screen, (255,0,255), bg_rect)

            ins_title = self.font_inst_title.render("Instructions", True, (0, 0, 0))
            def get_sp(x: int, y: int):
                surf = self.renderer.get_sprite(x, y)
                if surf:
                    return pygame.transform.scale(surf, (28, 28))
                return pygame.Surface((28, 28))

            pacman = get_sp(0, 0)
            blinky = get_sp(0, 4)
            pinky = get_sp(2, 4)
            inky = get_sp(4, 4)
            clyde = get_sp(6, 4)
            blink_ghost_white = get_sp(10, 4)

            pacman_txt = self.font_inst_regular.render("avoids", True, (0, 0, 0))

            self.screen.blit(ins_title, ins_title.get_rect(center=(cx, bg_rect.top + 50)))

            y_pos = bg_rect.top + 100
            pygame.draw.rect(self.screen, (0, 0, 0), (bg_rect.left + 10, y_pos + 10, 10, 10))
            self.screen.blit(pacman, pacman.get_rect(topleft=(bg_rect.left + 30, y_pos)))

            txt_rect = pacman_txt.get_rect(topleft=(bg_rect.left + 70, y_pos + 5))
            self.screen.blit(pacman_txt, txt_rect)

            ghost_x = txt_rect.right + 10
            self.screen.blit(blinky, blinky.get_rect(topleft=(ghost_x, y_pos)))
            self.screen.blit(pinky, pinky.get_rect(topleft=(ghost_x + 30, y_pos)))
            self.screen.blit(inky, inky.get_rect(topleft=(ghost_x + 60, y_pos)))
            self.screen.blit(clyde, clyde.get_rect(topleft=(ghost_x + 90, y_pos)))

            y_pos = bg_rect.top + 150
            dots_txt = self.font_inst_regular.render(f"DOTS SCORE {self.dot_power} POINTS", True, (0, 0, 0))
            pygame.draw.rect(self.screen, (0, 0, 0), (bg_rect.left + 10, y_pos + 10, 10, 10))
            pygame.draw.circle(self.screen, (128, 128, 128), [bg_rect.left + 35, y_pos + 15], 5)
            pygame.draw.circle(self.screen, (128, 128, 128), [bg_rect.left + 50, y_pos + 15], 5)
            pygame.draw.circle(self.screen, (128, 128, 128), [bg_rect.left + 65, y_pos + 15], 5)
            self.screen.blit(dots_txt, dots_txt.get_rect(topleft=(bg_rect.left + 85, y_pos + 5)))

            y_pos = bg_rect.top + 200
            pacgums_nb_txt = self.font_inst_regular.render(f"{self.pacgums_nb}", True, (0, 0, 0))
            pacgums_power_txt = self.font_inst_regular.render(f"FLASHING ENERGIZERS SCORE {self.pacgum_power} POINTS", True, (0, 0, 0))
            pygame.draw.rect(self.screen, (0, 0, 0), (bg_rect.left + 10, y_pos + 10, 10, 10))
            self.screen.blit(pacgums_nb_txt, pacgums_nb_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 5)))
            pygame.draw.circle(self.screen, (0, 0, 0), [bg_rect.left + 65, y_pos + 12], 10)
            self.screen.blit(pacgums_power_txt, pacgums_power_txt.get_rect(topleft=(bg_rect.left + 90, y_pos + 5)))

            y_pos = bg_rect.top + 250
            pygame.draw.rect(self.screen, (0, 0, 0), (bg_rect.left + 10, y_pos + 10, 10, 10))
            energezing_pc_txt = self.font_inst_regular.render(f"AFTER ENERGIZING", True, (0, 0, 0))
            energezing_ghost_txt = self.font_inst_regular.render(f"CAN ATTACK", True, (0, 0, 0))
            self.screen.blit(energezing_pc_txt, energezing_pc_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 5)))
            self.screen.blit(pacman, pacman.get_rect(topleft=(bg_rect.left + 225, y_pos)))
            self.screen.blit(energezing_ghost_txt, energezing_ghost_txt.get_rect(topleft=(bg_rect.left + 260, y_pos + 5)))
            self.screen.blit(blink_ghost_white, blink_ghost_white.get_rect(topleft=(bg_rect.left + 390, y_pos)))

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle keyboard and mouse input for menu navigation."""
        NUM_ITEMS = 4

        if self.state == "main":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_item = (self.selected_item + 1) % NUM_ITEMS
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_item = (self.selected_item - 1) % NUM_ITEMS
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self._activate_item(self.selected_item)
                elif event.key == pygame.K_1:
                    self._activate_item(0)
                elif event.key == pygame.K_2:
                    self._activate_item(1)
                elif event.key == pygame.K_3:
                    self._activate_item(2)
                elif event.key == pygame.K_4:
                    self._activate_item(3)
            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(self._menu_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_item = i
                        break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self._menu_rects):
                    if rect.collidepoint(event.pos):
                        self._activate_item(i)
                        break

        elif self.state == "instructions":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "main"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.state = "main"

    def _activate_item(self, index: int) -> None:
        """Execute the action for the selected menu item."""
        if index == 1:
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
