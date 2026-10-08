import pygame
import sys
import os
import time

from renderer import Render, MLXUtils
from ui_config import UIConfig


class Menu:
    def __init__(self, screen: pygame.Surface,
                 pacgums_power: int = 10,
                 super_pacgums_power: int = 50,
                 pacgums_nb: int = 4) -> None:

        # 1. Basic variables and configuration
        self.screen = screen
        self.state = "main"
        self.selected_item = 0
        self.anime_x = 1000

        self.pacgums_power = pacgums_power
        self.super_pacgums_power = super_pacgums_power
        self.pacgums_nb = pacgums_nb

        # 2. UI and drawing
        self.ui = UIConfig()
        self.renderer = Render()
        self._menu_rects: list[pygame.Rect] = []

        # 3. Varibles for animation and graphics
        self.last_anim_time = int(time.perf_counter() * 1000)
        self.anim_frame = 0
        self.pacman_frames: list[pygame.Surface] = []
        self._mute_icon: pygame.Surface | None = None
        self._mute_rect: pygame.Rect | None = None

        # Base dir for assets
        base_dir = getattr(
            sys, '_MEIPASS', os.path.join(os.path.dirname(__file__), "..")
            )
        assets = os.path.normpath(os.path.join(base_dir, "assets"))

        # -- Loading of files --

        # Spritesheet
        sheet_path = os.path.join(
            assets, "spritesheets", "main-spritesheet.png"
        )
        self.renderer.load_spritesheet(sheet_path)

        # Icon for mute sounds
        mute_path = os.path.join(assets, "others", "volume-mute.png")
        try:
            img = pygame.image.load(mute_path).convert_alpha()
            self._mute_icon = MLXUtils.scale_image(img, 32, 32)
        except pygame.error:
            pass

    def draw_main_menu(self, top_scores: list = None, audio=None) -> None:
        self.screen.fill((0, 0, 0))

        # Helper function for getting assets (used by both states)
        def get_sp(x: int, y: int):
            surf = self.renderer.get_sprite(x, y)
            if surf:
                scaled = MLXUtils.scale_image(surf, 28, 28)
                scaled.set_colorkey((255, 0, 255))
                return scaled
            return pygame.Surface((28, 28))

        # Populate animation frames if empty (using spritesheet)
        if not self.pacman_frames:
            self.pacman_frames = [
                get_sp(0, 0),  # open mouth left
                get_sp(0, 2),  # half-open mouth left
                get_sp(8, 0)   # closed mouth
            ]

        # Animation logic (used by main state)
        current_time = int(time.perf_counter() * 1000)
        if current_time - self.last_anim_time >= 100:
            self.last_anim_time = current_time
            self.anim_frame = (self.anim_frame + 1) % len(self.pacman_frames)

        pacman = self.pacman_frames[self.anim_frame]

        blinky = get_sp(0, 8)
        pinky = get_sp(2, 8)
        inky = get_sp(4, 8)
        clyde = get_sp(6, 8)

        if self.state == "main":
            cx = self.screen.get_width() // 2
            cy = self.screen.get_height() // 2

            # 1. Draw Title
            try:
                img = pygame.image.load("./assets/menu-nav/pac-man-logo.png")
                self.screen.blit(img, img.get_rect(center=(cx, cy - 200)))
            except (FileNotFoundError, pygame.error) as err:
                print("Couldn't load PACMAN title in menu, loading default text..")
                title = self.ui.font_title.render("Pac-Man", True, (253, 255, 0))
                self.screen.blit(title, title.get_rect(center=(cx - 5, cy - 200)))

            try:
                push_img = pygame.image.load("./assets/menu-nav/push-space.png")
                self.screen.blit(push_img, push_img.get_rect(center=(cx - 5, cy - 100)))
            except (FileNotFoundError, pygame.error):
                pass
                # self.ui.draw_pulsing_nav(self.screen, "Push SPACE for play", cx - 5, cy + 200)


            # 2. Draw Menu Items & Pointer
            self._menu_rects = []
            menu_items = [
                ("view-highscore.png", "view-highscore-hover.png"),
                ("instructions.png", "instructions-hover.png"),
                ("exit.png", "exit-hover.png")
            ]

            for i, (normal_img, hover_img) in enumerate(menu_items):
                img_name = hover_img if i == self.selected_item else normal_img
                try:
                    surf = pygame.image.load(f"./assets/menu-nav/{img_name}")
                except (FileNotFoundError, pygame.error):
                    labels = ["View Highscores", "Instructions", "Exit"]
                    color = self.ui.C_TEXT_PURPLE if i == self.selected_item else self.ui.C_TEXT_WHITE
                    surf = self.ui.font_regular.render(labels[i], True, color)

                rect = surf.get_rect(center=(cx, cy - 35 + (i * 50)))
                self._menu_rects.append(rect)
                self.screen.blit(surf, rect)

            # 3. Draw Top 4 Highscores
            if top_scores:
                try:
                    top_scores_img = pygame.image.load("./assets/menu-nav/highscores.png")
                    self.screen.blit(top_scores_img, top_scores_img.get_rect(center=(cx, cy + 120)))
                except (FileNotFoundError, pygame.error):
                    hs_title = self.ui.font_regular.render("TOP SCORES", True, (253, 255, 0))
                    self.screen.blit(hs_title, hs_title.get_rect(center=(cx, cy + 120)))
                for idx, hs in enumerate(top_scores):
                    text = f"{idx + 1}. {hs['name']} - {hs['score']} pts"
                    surf = self.ui.font_regular.render(text, True, (255, 255, 255))
                    self.screen.blit(surf, surf.get_rect(center=(cx + 10, cy + 155 + (idx * 25))))

            # 4. Draw Animation
            start_x = cx - 90
            y_pos = cy + 280

            if self.anime_x > start_x:
                self.anime_x -= 8
            else:
                self.anime_x = start_x

            # Draw only once per frame at the current position
            MLXUtils.draw_circle(self.screen, (255,255,255), (int(self.anime_x), int(y_pos + 15)), 5)
            self.screen.blit(pacman, (self.anime_x + 36, y_pos))
            self.screen.blit(clyde, (self.anime_x + 76, y_pos))
            self.screen.blit(blinky, (self.anime_x + 108, y_pos))
            self.screen.blit(pinky, (self.anime_x + 144, y_pos))
            self.screen.blit(inky, (self.anime_x + 180, y_pos))

            self._instruction_rect = self._menu_rects[2]

            # Draw mute icon in top-right corner
            self._draw_mute_icon(audio)

        elif self.state == "instructions":
            cx = self.screen.get_width() // 2
            cy = self.screen.get_height() // 2

            # --- Panel ---
            bg_rect = self.ui.draw_panel_bg(self.screen, cx, cy)

            ins_title = self.ui.font_inst_title.render("INTRUCTIONS", True, self.ui.C_TEXT_WHITE)
            blink_ghost_white = get_sp(10, 4)
            pacman_txt = self.ui.font_inst_regular.render("AVOIDS", True, self.ui.C_TEXT_WHITE)
            self.screen.blit(ins_title, ins_title.get_rect(center=(cx, bg_rect.top + 20)))

            self._close_rect = self.ui.draw_close_button(self.screen, bg_rect)


            y_pos = bg_rect.top + 70
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)

            pacman_rect = pacman.get_rect(topleft=(bg_rect.left + 30, y_pos))
            self.screen.blit(pacman, pacman_rect)

            # Vertically center the AVOIDS text to pacman
            txt_rect = pacman_txt.get_rect(left=bg_rect.left + 70, centery=pacman_rect.centery)
            self.screen.blit(pacman_txt, txt_rect)

            ghost_x = txt_rect.right + 10
            # Also vertically center the ghosts to pacman
            self.screen.blit(blinky, blinky.get_rect(left=ghost_x, centery=pacman_rect.centery))
            self.screen.blit(pinky, pinky.get_rect(left=ghost_x + 30, centery=pacman_rect.centery))
            self.screen.blit(inky, inky.get_rect(left=ghost_x + 60, centery=pacman_rect.centery))
            self.screen.blit(clyde, clyde.get_rect(left=ghost_x + 90, centery=pacman_rect.centery))

            y_pos = bg_rect.top + 120
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            dots_txt = self.ui.font_inst_regular.render(f"PACGUMS SCORE {self.pacgums_power} POINTS", True, self.ui.C_TEXT_WHITE)
            MLXUtils.draw_circle(self.screen, self.ui.C_TEXT_WHITE, (int(bg_rect.left + 35), int(y_pos + 15)), 5)
            MLXUtils.draw_circle(self.screen, self.ui.C_TEXT_WHITE, (int(bg_rect.left + 50), int(y_pos + 15)), 5)
            MLXUtils.draw_circle(self.screen, self.ui.C_TEXT_WHITE, (int(bg_rect.left + 65), int(y_pos + 15)), 5)
            self.screen.blit(dots_txt, dots_txt.get_rect(topleft=(bg_rect.left + 85, y_pos + 5)))

            y_pos = bg_rect.top + 170
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            pacgums_nb_txt = self.ui.font_inst_regular.render(f"{self.pacgums_nb}", True, self.ui.C_TEXT_WHITE)
            pacgums_power_txt = self.ui.font_inst_regular.render(f"FLASHING SUPER PACGUMS SCORE {self.super_pacgums_power} POINTS", True, self.ui.C_TEXT_WHITE)
            self.screen.blit(pacgums_nb_txt, pacgums_nb_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 10)))
            MLXUtils.draw_circle(self.screen, self.ui.C_TEXT_WHITE, (int(bg_rect.left + 65), int(y_pos + 12)), 10)
            self.screen.blit(pacgums_power_txt, pacgums_power_txt.get_rect(topleft=(bg_rect.left + 90, y_pos + 10)))

            y_pos = bg_rect.top + 220
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)

            energezing_pc_txt = self.ui.font_inst_regular.render("AFTER POWER UP", True, self.ui.C_TEXT_WHITE)
            pc_rect = energezing_pc_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 10))
            self.screen.blit(energezing_pc_txt, pc_rect)

            pacman_rect = pacman.get_rect(left=pc_rect.right + 10, centery=pc_rect.centery)
            self.screen.blit(pacman, pacman_rect)

            energezing_ghost_txt = self.ui.font_inst_regular.render("CAN EAT", True, self.ui.C_TEXT_WHITE)
            ghost_txt_rect = energezing_ghost_txt.get_rect(left=pacman_rect.right + 10, centery=pc_rect.centery)
            self.screen.blit(energezing_ghost_txt, ghost_txt_rect)

            blink_rect = blink_ghost_white.get_rect(left=ghost_txt_rect.right + 10, centery=pc_rect.centery)
            self.screen.blit(blink_ghost_white, blink_rect)

            y_pos = bg_rect.top + 270
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            controls_txt = self.ui.font_inst_regular.render("CONTROLS: [W][A][S][D] OR ARROWS TO MOVE", True, self.ui.C_TEXT_WHITE)
            self.screen.blit(controls_txt, controls_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 10)))

            # Added Pause Instructions
            y_pos = bg_rect.top + 310
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            pause_txt = self.ui.font_inst_regular.render("PAUSE: PRESS [P] OR [SPACE]", True, self.ui.C_TEXT_WHITE)
            self.screen.blit(pause_txt, pause_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 10)))

            # Pulsing ESC hint
            try:
                ret_img = pygame.image.load("./assets/return-instuctions.png")
                self.screen.blit(ret_img, ret_img.get_rect(center=(cx, bg_rect.bottom + 50)))
            except (FileNotFoundError, pygame.error):
                pass



    def _draw_mute_icon(self, audio=None) -> None:
        """Draw volume-mute icon in top-right corner; red tint when muted."""
        if self._mute_icon is None:
            return
        margin = 12
        icon_size = 32
        x = self.screen.get_width() - icon_size - margin
        y = margin
        self._mute_rect = pygame.Rect(x, y, icon_size, icon_size)

        is_muted = audio.muted if audio else False

        if is_muted:
            # Apply red tint manually
            icon = MLXUtils.colorize_icon(self._mute_icon, 220, 50, 50)
            self.screen.blit(icon, (x, y))
            # Draw a diagonal strike-through line
            MLXUtils.draw_line(self.screen, (220, 50, 50), (x + 4, y + icon_size - 4), (x + icon_size - 4, y + 4), 3)
        else:
            # Apply white tint manually
            icon = MLXUtils.colorize_icon(self._mute_icon, 255, 255, 255)
            self.screen.blit(icon, (x, y))

    def handle_event(self, event: pygame.event.Event, audio=None) -> None:
        """Handle keyboard and mouse input for menu navigation."""
        NUM_ITEMS = 3

        if self.state == "main":
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_item = (self.selected_item + 1) % NUM_ITEMS
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_item = (self.selected_item - 1) % NUM_ITEMS
                elif event.key == pygame.K_m and audio:
                    audio.toggle_mute()
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
                # Check mute icon click
                if self._mute_rect and self._mute_rect.collidepoint(event.pos) and audio:
                    audio.toggle_mute()
                    return
                for i, rect in enumerate(self._menu_rects):
                    if rect.collidepoint(event.pos):
                        self._activate_item(i + 1)
                        break

        elif self.state == "instructions":
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
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

    last_time = time.perf_counter()
    while True:
        current_time = time.perf_counter()
        dt = current_time - last_time
        if dt < (1.0 / 60.0):
            time.sleep((1.0 / 60.0) - dt)
            current_time = time.perf_counter()
            dt = current_time - last_time
        last_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            menu.handle_event(event)

        menu.draw_main_menu()
        pygame.display.flip()
