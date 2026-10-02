import pygame
import sys
from ui_config import UIConfig
from game_state import State

class PauseMenu:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.ui = UIConfig()
        self.selected_item = 0
        self._menu_rects = []

    def run(self, app) -> None:
        """Draw and handle pause screen waiting for keypress."""
        if app.is_eval:
            labels = [
                "Resume Game",
                "Return to main menu",
                "-- CHEATS --",
                f"Level: < {app.game_state.current_level_idx + 1} >",
                f"Invincibility: < {'ON' if app.invincible else 'OFF'} >",
                f"Pac-Man Speed: < {app.player.speed:.1f} >",
                f"Blinky Speed: < {app.blinky.speed:.1f} >",
                f"Pinky Speed: < {app.pinky.speed:.1f} >",
                f"Inky Speed: < {app.inky.speed:.1f} >",
                f"Clyde Speed: < {app.clyde.speed:.1f} >",
                f"Lives: < {app.game_state.lives} >",
                "Reset to defaults",
            ]
            separator_idx = 2
        else:
            labels = ["Resume Game", "Return to main menu"]
            separator_idx = -1

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.VIDEORESIZE:
                app.render.resize(ev.w, ev.h)
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_w, pygame.K_UP):
                    self.selected_item = (self.selected_item - 1) % len(labels)
                    if app.is_eval and self.selected_item == separator_idx:
                        self.selected_item = separator_idx - 1
                elif ev.key in (pygame.K_s, pygame.K_DOWN):
                    self.selected_item = (self.selected_item + 1) % len(labels)
                    if app.is_eval and self.selected_item == separator_idx:
                        self.selected_item = separator_idx + 1
                elif ev.key == pygame.K_SPACE:
                    app.app_state = "PLAYING"
                    app.audio.stop_bgm()
                elif ev.key in (pygame.K_RETURN, pygame.K_p):
                    self._execute_pause_action(app)
                elif ev.key in (pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT):
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
                            if app.is_eval and 3 <= i <= 10:
                                self._adjust_cheat_value(app, pygame.K_RIGHT)
                            else:
                                self._execute_pause_action(app)

        # 1. Redraw maze, entities, hud via app.render
        app.render.screen.fill((20, 20, 40))
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

        app.render.draw_player(app.player.grid_x, app.player.grid_y, app.player.current_dir, 0.0)
        for g in app.ghosts:
            app.render.draw_ghost(g.grid_x, g.grid_y, g.color_name, g.state.value, app.game_state.frigthened_timer)

        mode_text = "SCATTER" if app.is_scatter_wave else "CHASE"
        if app.game_state.is_frightened:
            mode_text = "FLEE"

        cheat_str = ""
        if app.is_eval:
            inv = "ON" if app.invincible else "OFF"
            cheat_str = (f"INV: {inv} | SPEEDS: Pac-Man: {app.player.speed:.1f} | "
                         f"Blinky: {app.blinky.speed:.1f} | Pinky: {app.pinky.speed:.1f} | "
                         f"Inky: {app.inky.speed:.1f} | Clyde: {app.clyde.speed:.1f}")

        app.render.draw_hud(
            app.game_state.score, app.game_state.lives, app.game_state.time_remaining,
            app.game_state.current_level_idx + 1, app.config.get("levels"),
            mode_text, app.is_eval, cheat_str
        )

        # 2. Draw pause overlay
        self.draw_overlay(labels, separator_idx)
        app.render.render_frame()

    def draw_overlay(self, labels: list[str], separator_idx: int) -> None:
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(210)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2

        title = self.ui.font_title.render("PAUSED", True, self.ui.C_TEXT_YELLOW)
        self.screen.blit(title, title.get_rect(center=(cx, cy - 200)))
        
        self._menu_rects = []
        start_y = cy - 110

        for i, label in enumerate(labels):
            if i == separator_idx:
                sep_surf = self.ui.font_inst_title.render(label, True, self.ui.C_TEXT_YELLOW)
                self.screen.blit(sep_surf, sep_surf.get_rect(center=(cx, start_y + (i * 35))))
                self._menu_rects.append(sep_surf.get_rect(center=(cx, start_y + (i * 35))))
                continue

            color = self.ui.C_TEXT_CYAN if i == self.selected_item else (self.ui.C_CLOSE_HOVER if "OFF" in label else self.ui.C_TEXT_WHITE)
            surf = self.ui.font_regular.render(label, True, color)
            rect = surf.get_rect(center=(cx, start_y + (i * 35)))
            self._menu_rects.append(rect)
            self.screen.blit(surf, rect)

            if i == self.selected_item:
                mid_y = rect.centery
                tip_x = rect.left - 15
                self.ui.draw_bullet(self.screen, tip_x, mid_y, color=color, is_centered=True)

    def _execute_pause_action(self, app) -> None:
        if self.selected_item == 0:
            app.app_state = "PLAYING"
            app.audio.stop_bgm()
        elif self.selected_item == 1:
            app.app_state = "MENU"
        elif app.is_eval:
            if self.selected_item == 3:
                app.game_state.state = State.LEVEL_TRANSITION
                app.app_state = "PLAYING"
            elif self.selected_item == 4:
                app.invincible = not app.invincible
            elif self.selected_item == 11:
                self._reset_cheats_to_defaults(app)

    def _adjust_cheat_value(self, app, key: int) -> None:
        if not app.is_eval:
            return
        diff = -0.5 if key in (pygame.K_a, pygame.K_LEFT) else 0.5
        idx = self.selected_item
        if idx == 3:
            lvl_diff = -1 if diff < 0 else 1
            max_lvl = app.config.get("levels")
            new_lvl = app.game_state.current_level_idx + lvl_diff
            if 0 <= new_lvl < max_lvl:
                app.game_state.current_level_idx = new_lvl
                app.game_state.state = State.LEVEL_TRANSITION
        elif idx == 4:
            app.invincible = not app.invincible
        elif idx == 5:
            app.player.speed = max(0.0, min(10.0, app.player.speed + diff))
            app.custom_player_speed = app.player.speed
        elif idx == 6:
            app.blinky.speed = max(0.0, min(10.0, app.blinky.speed + diff))
            app.custom_ghost_speeds['blinky'] = app.blinky.speed
        elif idx == 7:
            app.pinky.speed = max(0.0, min(10.0, app.pinky.speed + diff))
            app.custom_ghost_speeds['pinky'] = app.pinky.speed
        elif idx == 8:
            app.inky.speed = max(0.0, min(10.0, app.inky.speed + diff))
            app.custom_ghost_speeds['inky'] = app.inky.speed
        elif idx == 9:
            app.clyde.speed = max(0.0, min(10.0, app.clyde.speed + diff))
            app.custom_ghost_speeds['clyde'] = app.clyde.speed
        elif idx == 10:
            lives_diff = -1 if diff < 0 else 1
            app.game_state.lives = max(1, app.game_state.lives + lives_diff)

    def _reset_cheats_to_defaults(self, app) -> None:
        app.invincible = False
        app.custom_player_speed = None
        app.custom_ghost_speeds.clear()
        app.player.speed = 5.0

        max_levels = app.config.get("levels")
        start_speed = 1.0
        end_speed = 5.2
        if max_levels > 1:
            speed_incr = (end_speed - start_speed) / (max_levels - 1)
            cur_speed = start_speed + (speed_incr * app.game_state.current_level_idx)
        else:
            cur_speed = start_speed

        app.blinky.speed = cur_speed
        app.pinky.speed = cur_speed
        app.inky.speed = cur_speed
        app.clyde.speed = cur_speed
        app.game_state.lives = app.config.get("lives")
