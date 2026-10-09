import pygame
import sys

from ui_config import UIConfig
from game_state import State
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import Application


class PauseMenu:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.ui = UIConfig()

        self.selected_item = 0
        self._menu_rects: list[pygame.Rect] = []

    def run(self, app: "Application") -> None:
        """Draw and handle pause screen waiting for keypress."""
        mute_label = f"MUTE SOUND: < {'ON' if app.audio.muted else 'OFF'} >"
        if app.is_eval:
            labels = [
                "RESUME GAME",
                "RETURN TO MAIN MENU",
                mute_label,
                "-- CHEATS --",
                f"LEVEL: < {app.game_state.current_level_idx + 1} >",
                f"INVINCIBILITY: < {'ON' if app.invincible else 'OFF'} >",
                f"PAC-MAN SPEED: < {app.player.speed:.1f} >",
                f"BLINKY SPEED: < {app.blinky.speed:.1f} >",
                f"PINKY SPEED: < {app.pinky.speed:.1f} >",
                f"INKY SPEED: < {app.inky.speed:.1f} >",
                f"CLYDE SPEED: < {app.clyde.speed:.1f} >",
                f"LIVES: < {app.game_state.lives} >",
                "RESET TO DEFAULTS",
            ]
            separator_idx = 3
        else:
            labels = ["Resume Game", "Return to main menu", mute_label]
            separator_idx = -1

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_w, pygame.K_UP):
                    self.selected_item = (self.selected_item - 1) % len(labels)
                    if app.is_eval and self.selected_item == separator_idx:
                        self.selected_item = separator_idx - 1
                elif ev.key in (pygame.K_s, pygame.K_DOWN):
                    self.selected_item = (self.selected_item + 1) % len(labels)
                    if app.is_eval and self.selected_item == separator_idx:
                        self.selected_item = separator_idx + 1
                elif ev.key == pygame.K_m:
                    app.audio.toggle_mute()
                elif ev.key == pygame.K_SPACE:
                    app.app_state = "PLAYING"
                    app.audio.stop_bgm()
                elif ev.key in (pygame.K_RETURN, pygame.K_p):
                    self._execute_pause_action(app)
                elif ev.key in (pygame.K_a, pygame.K_LEFT,
                                pygame.K_d, pygame.K_RIGHT):
                    self._adjust_cheat_value(app, ev.key)
            elif ev.type == pygame.MOUSEMOTION:
                mouse_pos = ev.pos
                for i, rect in enumerate(self._menu_rects):
                    if rect.collidepoint(mouse_pos) and i != separator_idx:
                        self.selected_item = i
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1:
                    mouse_pos = ev.pos
                    for i, rect in enumerate(self._menu_rects):
                        if rect.collidepoint(mouse_pos) and i != separator_idx:
                            self.selected_item = i
                            if app.is_eval and i in (4, 6, 7, 8, 9, 10, 11):
                                font = self.ui.font_regular
                                prefix = labels[i].split("<", 1)[0]

                                pref_w = font.size(prefix)[0]
                                arr_w = font.size("<")[0] // 2
                                mx = mouse_pos[0]

                                left_x = rect.left + pref_w + arr_w
                                right_x = rect.right - arr_w

                                if abs(mx - left_x) < abs(mx - right_x):
                                    key = pygame.K_LEFT
                                else:
                                    key = pygame.K_RIGHT

                                self._adjust_cheat_value(app, key)
                            else:
                                self._execute_pause_action(app)

        app.render.screen.fill(self.ui.GAME_PATH)
        for y, row in enumerate(app.grid):
            for x, cell in enumerate(row):
                if cell == 0:
                    app.render.draw_wall(x, y)
                elif cell == 4:
                    app.render.draw_wall(x, y, is_logo=True)
                elif cell == 2:
                    app.render.draw_pacgum(x, y)
                elif cell == 3:
                    app.render.draw_powergum(x, y)
        app.render.draw_walls_grid(app.grid)

        app.render.draw_player(app.player.grid_x, app.player.grid_y,
                               app.player.current_dir, 0.0)
        draw_ghost = app.render.draw_ghost
        timer = app.game_state.frigthened_timer
        for g in app.ghosts:
            draw_ghost(g.grid_x, g.grid_y, g.color_name,
                       g.state.value, timer)

        mode_text = "SCATTER" if app.is_scatter_wave else "CHASE"
        if app.game_state.is_frightened:
            mode_text = "FLEE"

        cheat_str = ""
        if app.is_eval:
            inv = "ON" if app.invincible else "OFF"
            cheat_str = " | ".join([
                f"INV: {inv}",
                f"SPEEDS: Pac-Man: {app.player.speed:.1f}",
                f"Blinky: {app.blinky.speed:.1f}",
                f"Pinky: {app.pinky.speed:.1f}",
                f"Inky: {app.inky.speed:.1f}",
                f"Clyde: {app.clyde.speed:.1f}"
            ])

        gs = app.game_state
        app.render.draw_hud(
            gs.score, gs.lives, gs.time_remaining,
            gs.current_level_idx + 1, app.config.get("levels"),
            mode_text, app.is_eval, cheat_str
        )

        self.draw_overlay(labels, separator_idx)
        app.render.render_frame()

    def draw_overlay(self, labels: list[str], separator_idx: int) -> None:
        width, height = self.screen.get_width(), self.screen.get_height()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        self.screen.blit(overlay, (0, 0))

        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2

        try:
            surf = pygame.image.load("./assets/pause-icon.png")
            # If the user wants scaling like in ready-photo, we can apply it here
            from renderer import MLXUtils
            title = MLXUtils.scale_image(surf, 200, 200)
        except (FileNotFoundError, pygame.error, ImportError):
            color = self.ui.C_TEXT_YELLOW
            title = self.ui.font_regular.render("PAUSED", True, color)

        self.screen.blit(title, title.get_rect(center=(cx, cy - 200)))

        self._menu_rects = []
        start_y = cy - 110
        pause_text = self.ui.font_regular

        for i, label in enumerate(labels):
            if i == separator_idx:
                if i == 3:
                    sep_surf = pause_text.render(label, True, self.ui.C_TEXT_YELLOW)
                else:
                    sep_surf = pause_text.render(label, True, color)
                y_pos = start_y + (i * 35)
                rect = sep_surf.get_rect(center=(cx, y_pos - 10))
                self.screen.blit(sep_surf, rect)
                self._menu_rects.append(rect)
                continue

            is_mute_item = label.startswith("Mute Sound")
            is_muted_on = is_mute_item and "ON" in label
            color_muted = self.ui.C_CLOSE_HOVER
            if i == self.selected_item:
                color = color_muted if is_muted_on else self.ui.C_TEXT_PURPLE
            elif is_muted_on:
                color = color_muted
            else:
                color = self.ui.C_TEXT_WHITE
            surf = self.ui.font_regular.render(label, True, color)
            rect = surf.get_rect(center=(cx, start_y + (i * 30)))
            self._menu_rects.append(rect)
            self.screen.blit(surf, rect)

    def _execute_pause_action(self, app: "Application") -> None:
        if self.selected_item == 0:
            app.app_state = "PLAYING"
            app.audio.stop_bgm()
        elif self.selected_item == 1:
            app.app_state = "MENU"
        elif self.selected_item == 2:
            app.audio.toggle_mute()
        elif app.is_eval:
            if self.selected_item == 4:
                app.game_state.state = State.LEVEL_TRANSITION
                app.app_state = "PLAYING"
            elif self.selected_item == 5:
                app.invincible = not app.invincible
            elif self.selected_item == 12:
                self._reset_cheats_to_defaults(app)

    def _adjust_cheat_value(self, app: "Application", key: int) -> None:
        idx = self.selected_item
        if idx == 2:
            app.audio.toggle_mute()
            return

        if not app.is_eval:
            return
        diff = -0.5 if key in (pygame.K_a, pygame.K_LEFT) else 0.5
        if idx == 4:
            lvl_diff = -1 if diff < 0 else 1
            max_lvl = app.config.get("levels")
            new_lvl = app.game_state.current_level_idx + lvl_diff
            if 0 <= new_lvl < max_lvl:
                app.game_state.current_level_idx = new_lvl
                app.game_state.state = State.LEVEL_TRANSITION
        elif idx == 5:
            app.invincible = not app.invincible
        elif idx == 6:
            app.player.speed = max(0.0, min(10.0, app.player.speed + diff))
            app.custom_player_speed = app.player.speed
        elif idx == 7:
            app.blinky.speed = max(0.0, min(10.0, app.blinky.speed + diff))
            app.custom_ghost_speeds['blinky'] = app.blinky.speed
        elif idx == 8:
            app.pinky.speed = max(0.0, min(10.0, app.pinky.speed + diff))
            app.custom_ghost_speeds['pinky'] = app.pinky.speed
        elif idx == 9:
            app.inky.speed = max(0.0, min(10.0, app.inky.speed + diff))
            app.custom_ghost_speeds['inky'] = app.inky.speed
        elif idx == 10:
            app.clyde.speed = max(0.0, min(10.0, app.clyde.speed + diff))
            app.custom_ghost_speeds['clyde'] = app.clyde.speed
        elif idx == 11:
            lives_diff = -1 if diff < 0 else 1
            app.game_state.lives = max(1, app.game_state.lives + lives_diff)

    def _reset_cheats_to_defaults(self, app: "Application") -> None:
        app.invincible = False
        app.custom_player_speed = None
        app.custom_ghost_speeds.clear()
        app.player.speed = 5.0

        max_levels = app.config.get("levels")
        start_speed = 1.0
        end_speed = 5.2
        if max_levels > 1:
            lvl_idx = app.game_state.current_level_idx
            speed_incr = (end_speed - start_speed) / (max_levels - 1)
            cur_speed = start_speed + (speed_incr * lvl_idx)
        else:
            cur_speed = start_speed

        app.blinky.speed = cur_speed
        app.pinky.speed = cur_speed
        app.inky.speed = cur_speed
        app.clyde.speed = cur_speed
        app.game_state.lives = app.config.get("lives")
