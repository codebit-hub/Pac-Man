import pygame
import sys
import os
import time
from typing import Optional, Any

from renderer import Render, MLXUtils
from ui_config import UIConfig


class Menu:
    """Manages the main menu screens, submenus, and start-up animations."""

    def __init__(self, screen: pygame.Surface,
                 pacgums_power: int = 10,
                 super_pacgums_power: int = 50,
                 pacgums_nb: int = 4) -> None:
        """Initialize the menu with rendering surfaces"""

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
            sys, '_MEIPASS', os.path.join(
                os.path.dirname(__file__), ".."))
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

    def draw_main_menu(self, top_scores: Optional[list] = None,
                       audio: Optional[Any] = None) -> None:
        """Draws the main menu with high scores and settings"""
        self.screen.fill((0, 0, 0))

        # Helper functions for spitesheets
        def get_sp(x: int, y: int) -> pygame.Surface:
            """Extracts and scales a specific sprite for the menu animation."""
            surf = self.renderer.get_sprite(x, y)
            if surf:
                scaled = MLXUtils.scale_image(surf, 28, 28)
                scaled.set_colorkey((255, 0, 255))
                return scaled  # type: ignore[no-any-return]
            return pygame.Surface((28, 28))

        # Animation of pacman in menu
        if not self.pacman_frames:
            self.pacman_frames = [
                get_sp(0, 0),  # open mouth left
                get_sp(0, 2),  # half-open mouth left
                get_sp(8, 0)   # closed mouth
            ]

        # Animation logic
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
            except (FileNotFoundError, pygame.error):
                print("Couldn't load PACMAN title, loading default text..")
                c = self.ui.C_TEXT_YELLOW
                title = self.ui.font_regular.render("Pac-Man", True, c)
                rect = title.get_rect(center=(cx - 5, cy - 200))
                self.screen.blit(title, rect)

            try:
                img = pygame.image.load("./assets/menu-nav/push-space.png")
                self.screen.blit(img, img.get_rect(center=(cx - 5, cy - 100)))
            except (FileNotFoundError, pygame.error):
                pass

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
                    c = (self.ui.C_TEXT_PURPLE if i == self.selected_item
                         else self.ui.C_TEXT_WHITE)
                    surf = self.ui.font_regular.render(labels[i], True, c)

                rect = surf.get_rect(center=(cx, cy - 35 + (i * 50)))
                self._menu_rects.append(rect)
                self.screen.blit(surf, rect)

            # 3. Draw Top 4 Highscores
            if top_scores:
                try:
                    img_path = "./assets/menu-nav/highscores.png"
                    top_scores_img = pygame.image.load(img_path)
                    rect = top_scores_img.get_rect(center=(cx, cy + 120))
                    self.screen.blit(top_scores_img, rect)
                except (FileNotFoundError, pygame.error):
                    c = (253, 255, 0)
                    hs_title = self.ui.font_regular.render(
                        "TOP SCORES", True, c)
                    rect = hs_title.get_rect(center=(cx, cy + 120))
                    self.screen.blit(hs_title, rect)
                for idx, hs in enumerate(top_scores):
                    text = f"{idx + 1}. {hs['name']} - {hs['score']} pts"
                    surf = self.ui.font_regular.render(
                        text, True, (255, 255, 255))
                    y = cy + 155 + (idx * 25)
                    rect = surf.get_rect(center=(cx + 10, y))
                    self.screen.blit(surf, rect)

            # 4. Draw Animation
            start_x = cx - 90
            y_pos = cy + 280

            if self.anime_x > start_x:
                self.anime_x -= 8
            else:
                self.anime_x = start_x

            # Draw only once per frame at the current position
            c_pos = (self.anime_x, y_pos + 15)
            MLXUtils.draw_circle(self.screen, self.ui.C_TEXT_WHITE, c_pos, 5)
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
            white = self.ui.C_TEXT_WHITE

            # --- Panel ---
            bg_rect = self.ui.draw_panel_bg(self.screen, cx, cy)

            ins_title = self.ui.font_regular.render("INTRUCTIONS", True, white)
            blink_ghost_white = get_sp(10, 4)
            pacman_txt = self.ui.font_regular.render("AVOIDS", True, white)
            rect = ins_title.get_rect(center=(cx, bg_rect.top + 20))
            self.screen.blit(ins_title, rect)

            self._close_rect = self.ui.draw_close_button(self.screen, bg_rect)

            y_pos = bg_rect.top + 70
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)

            pacman_rect = pacman.get_rect(topleft=(bg_rect.left + 30, y_pos))
            self.screen.blit(pacman, pacman_rect)

            # Vertically center the AVOIDS text to pacman
            centery = pacman_rect.centery
            rect = pacman_txt.get_rect(left=bg_rect.left + 70, centery=centery)
            self.screen.blit(pacman_txt, rect)

            ghost_x = rect.right + 10
            # Also vertically center the ghosts to pacman
            rect = blinky.get_rect(left=ghost_x, centery=centery)
            self.screen.blit(blinky, rect)
            rect = pinky.get_rect(left=ghost_x + 30, centery=centery)
            self.screen.blit(pinky, rect)
            rect = inky.get_rect(left=ghost_x + 60, centery=centery)
            self.screen.blit(inky, rect)
            rect = clyde.get_rect(left=ghost_x + 90, centery=centery)
            self.screen.blit(clyde, rect)

            y_pos = bg_rect.top + 120
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            txt = f"PACGUMS SCORE {self.pacgums_power} POINTS"
            dots_txt = self.ui.font_regular.render(txt, True, white)
            y_c = y_pos + 15
            screen = self.screen
            MLXUtils.draw_circle(screen, white, (bg_rect.left + 35, y_c), 5)
            MLXUtils.draw_circle(screen, white, (bg_rect.left + 50, y_c), 5)
            MLXUtils.draw_circle(screen, white, (bg_rect.left + 65, y_c), 5)
            rect = dots_txt.get_rect(topleft=(bg_rect.left + 85, y_pos + 5))
            self.screen.blit(dots_txt, rect)

            y_pos = bg_rect.top + 170
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            nb_txt = self.ui.font_regular.render(
                f"{self.pacgums_nb}", True, white)
            pt_txt = "FLASHING SUPER PACGUMS SCORE "
            f"{self.super_pacgums_power} POINTS"
            pwr_txt = self.ui.font_regular.render(pt_txt, True, white)
            rect = nb_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 10))
            self.screen.blit(nb_txt, rect)
            c_pos = (bg_rect.left + 65, y_pos + 12)
            MLXUtils.draw_circle(self.screen, white, c_pos, 10)
            rect = pwr_txt.get_rect(topleft=(bg_rect.left + 90, y_pos + 10))
            self.screen.blit(pwr_txt, rect)

            y_pos = bg_rect.top + 220
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)

            energezing_pc_txt = self.ui.font_regular.render(
                "AFTER POWER UP", True, white)
            pc_rect = energezing_pc_txt.get_rect(
                topleft=(bg_rect.left + 30, y_pos + 10))
            self.screen.blit(energezing_pc_txt, pc_rect)

            pacman_rect = pacman.get_rect(
                left=pc_rect.right + 10, centery=pc_rect.centery)
            self.screen.blit(pacman, pacman_rect)

            energezing_ghost_txt = self.ui.font_regular.render(
                "CAN EAT", True, white)
            ghost_txt_rect = energezing_ghost_txt.get_rect(
                left=pacman_rect.right + 10, centery=pc_rect.centery)
            self.screen.blit(energezing_ghost_txt, ghost_txt_rect)

            blink_rect = blink_ghost_white.get_rect(
                left=ghost_txt_rect.right + 10, centery=pc_rect.centery)
            self.screen.blit(blink_ghost_white, blink_rect)

            y_pos = bg_rect.top + 270
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            controls_txt = self.ui.font_regular.render(
                "CONTROLS: [W][A][S][D] OR ARROWS TO MOVE", True, white)
            rect = controls_txt.get_rect(
                topleft=(bg_rect.left + 30, y_pos + 10))
            self.screen.blit(controls_txt, rect)

            # Added Pause Instructions
            y_pos = bg_rect.top + 310
            self.ui.draw_bullet(self.screen, bg_rect.left + 20, y_pos)
            pause_txt = self.ui.font_regular.render(
                "PAUSE: PRESS [P] OR [SPACE]", True, white)
            rect = pause_txt.get_rect(topleft=(bg_rect.left + 30, y_pos + 10))
            self.screen.blit(pause_txt, rect)

            # Pulsing ESC hint
            try:
                ret_img = pygame.image.load("./assets/return-instuctions.png")
                rect = ret_img.get_rect(center=(cx, bg_rect.bottom + 50))
                self.screen.blit(ret_img, rect)
            except (FileNotFoundError, pygame.error):
                pass

    def _draw_mute_icon(self, audio: Optional[Any] = None) -> None:
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
            icon = MLXUtils.colorize_icon(self._mute_icon, 220, 50, 50)
            self.screen.blit(icon, (x, y))
        else:
            icon = MLXUtils.colorize_icon(self._mute_icon, 255, 255, 255)
            self.screen.blit(icon, (x, y))

    def handle_event(self, event: pygame.event.Event,
                     audio: Optional[Any] = None) -> None:
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
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
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
                if (self._mute_rect
                        and self._mute_rect.collidepoint(event.pos) and audio):
                    audio.toggle_mute()
                    return
                for i, rect in enumerate(self._menu_rects):
                    if rect.collidepoint(event.pos):
                        self._activate_item(i + 1)
                        break

        elif self.state == "instructions":
            if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                self.state = "main"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if (hasattr(self, "_close_rect")
                        and self._close_rect.collidepoint(event.pos)):
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
