"""Master execution script integrating Menu, Game, and Highscores."""

import os
import sys
import random
import pygame

from config import ConfigManager
from game_state import GameState, State
from highscore import HighScoreManager
from maze_loader import MazeLoader
from player import Player, Direction
from ghost import GhostState, Blinky, Pinky, Inky, Clyde
from renderer import Render
from menu import Menu


class Application:
    """Central app controller managing states and transitions."""

    def __init__(self, config_path: str) -> None:
        self.render = Render()
        self.config = ConfigManager()

        # Load config from argv
        self.config.load(config_path)

        lvl_w = self.config.get("level")[0]["width"]
        lvl_h = self.config.get("level")[0]["height"]
        self.render.setup_display((lvl_w * 2) + 1, (lvl_h * 2) + 1)
        self.screen = self.render.screen

        # Configurations & Highscores
        cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        self.config.load(cfg_path)

        self.game_state = GameState(self.config)
        self.highscores = HighScoreManager(self.config.get("highscore_filename"))

        # Setup Vokotera's Menu and Monkey-Patch the selections
        self.menu = Menu(self.screen)
        self.app_state = "MENU"
        # MENU, PLAYING, GAME_OVER, HIGHSCORES

        # New state variables
        self.pause_selected = 0
        self.input_name = ""

        # Store the original menu activate method
        self._og_activate = self.menu._activate_item

        def custom_activate(index: int) -> None:
            if index == 0:
                self._start_new_game()
            elif index == 1:
                self.app_state = "HIGHSCORES"
            elif index == 3:
                pygame.quit()
                sys.exit()
            else:
                self._og_activate(index)

        self.menu._activate_item = custom_activate

    def _start_new_game(self) -> None:
        """Initialize stats for a fresh run and load Level 1."""
        self.game_state.start_game()
        self._load_level()
        self.app_state = "PLAYING"

    def _load_level(self) -> None:
        """Generate maze, spawn entities, and prepare renderer."""
        self.loader = MazeLoader()

        # Pull base dimensions, can increase difficulty by scaling size later
        level_cfgs = self.config.get("level")

        # Use config.json level dimensions or default
        if self.game_state.current_level_idx < len(level_cfgs):
            lvl_cfg = level_cfgs[self.game_state.current_level_idx]
        else:
            lvl_cfg = {"width": 15, "height": 15}

        # Random seed for levels > 1
        if self.game_state.current_level_idx == 0:
            level_seed = self.config.get("seed")
        else:
            level_seed = random.randint(1, 999999)

        self.loader.generate(
            width=lvl_cfg["width"],
            height=lvl_cfg["height"],
            seed=level_seed,
            pacgum_count=self.config.get("pacgum")
        )
        self.grid = self.loader.get_grid()

        # Initialize Entities
        sp_x, sp_y = self.loader.spawn_point
        self.player = Player(sp_x, sp_y)
        self._init_ghosts()

        # Setup Renderer
        grid_w, grid_h = len(self.grid[0]), len(self.grid)

        # Update the existing renderer to dynamically scale the tile size
        self.render.setup_display(grid_w, grid_h)

        base = os.path.dirname(__file__)
        self.render.load_spritesheet(os.path.normpath(
            os.path.join(base, "..", "assets", "spritesheets", "main-spritesheet.png")))
        self.render.load_dot(os.path.normpath(
            os.path.join(base, "..", "assets", "others", "dot.png")))
        self.render.load_player_frames(os.path.normpath(
            os.path.join(base, "..", "assets", "pacman")))
        self.render.load_ghost_sprites()
        self.render.load_pacman_death()

        # Place into the game only the available pacgums based on empty corridors
        actual_pacgums = sum(row.count(2) for row in self.grid)
        self.game_state.setup_level(actual_pacgums)

        # Reset wave timers
        self.is_scatter_wave = True
        self.wave_timer = 7.0
        self.was_frightened = False

    def _init_ghosts(self) -> None:
        """Spawn ghosts with optional randomization."""
        w, h = len(self.grid[0]), len(self.grid)
        locs = [(w - 2, 1), (3, 1), (w - 2, h - 2), (1, h - 2)]

        # Adding ghost color randomization
        colors = ["Red", "Pink", "Cyan", "Orange"]

        if self.config.get("ghost_behavior_random"):
            random.shuffle(locs)
            random.shuffle(colors)

        # Calculate dynamic ghost speed: from 1.0 to 5.2 through levels
        max_levels = self.config.get("levels")
        start_speed = 1.0
        end_speed = 5.2

        if max_levels > 1:
            speed_incr = (end_speed - start_speed) / (max_levels - 1)
            cur_speed = start_speed + (
                speed_incr * self.game_state.current_level_idx)
        else:
            cur_speed = start_speed

        self.blinky = Blinky(locs[0][0], locs[0][1], speed=cur_speed)
        self.pinky = Pinky(locs[1][0], locs[1][1], speed=cur_speed)
        self.inky = Inky(locs[2][0], locs[2][1], speed=cur_speed)
        self.clyde = Clyde(locs[3][0], locs[3][1], speed=cur_speed)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]

        # Apply shuffled colors to ghosts
        for i, ghost in enumerate(self.ghosts):
            ghost.color_name = colors[i]

    def _play_death_anim(self, grid_x: int, grid_y: int) -> None:
        """Play Pac-Man death animation before respawn."""
        frames = self.render.pacman_death.get("frames", [])
        if not frames:
            pygame.time.wait(600)
            return
        clock = pygame.time.Clock()
        for frame_idx in range(len(frames)):
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    import sys; sys.exit()
            self.render.screen.fill((0, 0, 0))
            for gy, row in enumerate(self.grid):
                for gx, cell in enumerate(row):
                    if cell in (0, 4):
                        self.render.draw_wall(gx, gy, is_logo=(cell == 4))
                    elif cell == 2:
                        self.render.draw_pacgum(gx, gy)
                    elif cell == 3:
                        self.render.draw_powergum(gx, gy)
            self.render.draw_walls_grid(self.grid)
            self.render.draw_pacman_death(grid_x, grid_y, frame_idx)
            self.render.render_frame()
            clock.tick(12)
        pygame.time.wait(400)

    def _update_wave_timers(self, delta_time: float) -> None:
        """Manage Scatter/Chase and Flee modes from GameState."""
        if self.game_state.is_frightened:
            for g in self.ghosts:
                if g.state not in (GhostState.EATEN, GhostState.FLEE):
                    g.state = GhostState.FLEE
                    g.reverse_direction()
            self.was_frightened = True
            return

        # If frightened mode just ended, restore previous wave state
        if self.was_frightened:
            self.was_frightened = False
            tgt = GhostState.SCATTER if self.is_scatter_wave else GhostState.CHASE
            for g in self.ghosts:
                if g.state == GhostState.FLEE:
                    g.state = tgt

        # Standard Scatter/Chase Wave Toggle
        self.wave_timer -= delta_time
        if self.wave_timer <= 0:
            self.is_scatter_wave = not self.is_scatter_wave
            self.wave_timer = 7.0 if self.is_scatter_wave else 20.0
            tgt = GhostState.SCATTER if self.is_scatter_wave else GhostState.CHASE

            for g in self.ghosts:
                if g.state != GhostState.EATEN:
                    g.state = tgt
                    g.reverse_direction()

    def run(self) -> None:
        clock = pygame.time.Clock()
        while True:
            dt = clock.tick(60) / 1000.0

            if self.app_state == "MENU":
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif ev.type == pygame.VIDEORESIZE:
                        self.render.resize(ev.w, ev.h)
                    self.menu.handle_event(ev)
                # Pass top 4 scores to the menu
                top_4 = self.highscores.scores[:4]
                self.menu.draw_main_menu(top_4)
                pygame.display.flip()

            elif self.app_state == "PLAYING":
                self._run_game_frame(dt)

            elif self.app_state == "PAUSE":
                self._run_pause_frame()

            elif self.app_state == "NAME_INPUT":
                self._run_name_input_screen()

            elif self.app_state == "HIGHSCORES":
                self._run_highscore_screen()

    def _run_game_frame(self, dt: float) -> None:
        """Execute one frame of gameplay."""

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.VIDEORESIZE:
                self.render.resize(ev.w, ev.h)
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_w, pygame.K_UP):
                    self.player.set_direction(Direction.UP)
                elif ev.key in (pygame.K_s, pygame.K_DOWN):
                    self.player.set_direction(Direction.DOWN)
                elif ev.key in (pygame.K_a, pygame.K_LEFT):
                    self.player.set_direction(Direction.LEFT)
                elif ev.key in (pygame.K_d, pygame.K_RIGHT):
                    self.player.set_direction(Direction.RIGHT)
                elif ev.key in (pygame.K_p, pygame.K_SPACE):
                    self.app_state = "PAUSE"
                    self.pause_selected = 0
                    return

        # 1. Update State
        self.game_state.update(dt)
        self._update_wave_timers(dt)

        # Check for Level Transition or Death BEFORE moving entities
        if self.game_state.state == State.LEVEL_TRANSITION:
            self._load_level()
            return
        elif self.game_state.state in (State.GAME_OVER, State.VICTORY):
            # Transition to name input
            self.input_name = ""
            self.app_state = "NAME_INPUT"
            return

        self.player.update(dt, self.grid)

        for g in self.ghosts:
            g.update(
                dt, self.grid, self.player.grid_x, self.player.grid_y,
                self.player.current_dir, self.blinky.grid_x, self.blinky.grid_y
            )

        # 2. Consumption & Collisions
        px, py = self.player.grid_x, self.player.grid_y
        if self.grid[py][px] == 2:
            self.grid[py][px] = 1
            self.game_state.collect_pacgums()
        elif self.grid[py][px] == 3:
            self.grid[py][px] = 1
            self.game_state.collect_super_pacgum()

        for g in self.ghosts:
            if px == g.grid_x and py == g.grid_y:
                if g.state == GhostState.FLEE:
                    g.die()
                    self.game_state.eat_ghost()
                elif g.state in (GhostState.CHASE, GhostState.SCATTER):
                    self.game_state.lose_life()
                    if self.game_state.state != State.GAME_OVER:
                        self._play_death_anim(px, py)
                        self.player.respawn()
                        self._init_ghosts()
                    return

        # 3. Draw Frame
        self.render.screen.fill((20, 20, 40))
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == 0:
                    self.render.draw_wall(x, y)
                elif cell == 4:
                    self.render.draw_wall(x, y, is_logo=True)
                elif cell == 2:
                    self.render.draw_pacgum(x, y)
                elif cell == 3:
                    self.render.draw_powergum(x, y)
        self.render.draw_walls_grid(self.grid)

        self.render.draw_player(
            self.player.grid_x, self.player.grid_y, self.player.current_dir, dt
        )
        for g in self.ghosts:
            self.render.draw_ghost(
                g.grid_x, g.grid_y, g.color_name, g.state.value, self.game_state.frigthened_timer
            )

        # Determine text for the current wave mode
        mode_text = "SCATTER" if self.is_scatter_wave else "CHASE"
        if self.game_state.is_frightened:
            mode_text = "FLEE"

        self.render.draw_hud(
            self.game_state.score,
            self.game_state.lives,
            self.game_state.time_remaining,
            self.game_state.current_level_idx + 1,
            mode_text
        )

        self.render.render_frame()

    def _run_pause_frame(self) -> None:
        """Draw basic pause screen waiting for keypress."""

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.VIDEORESIZE:
                self.render.resize(ev.w, ev.h)
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN):
                    self.pause_selected = 1 - self.pause_selected
                elif ev.key == pygame.K_SPACE:
                    self.app_state = "PLAYING"
                elif ev.key in (pygame.K_RETURN, pygame.K_p):
                    if self.pause_selected == 0:
                        self.app_state = "PLAYING"
                    else:
                        self.app_state = "MENU"
            elif ev.type == pygame.MOUSEMOTION:
                mouse_pos = ev.pos
                if hasattr(self.render, '_menu_rects'):
                    for i, rect in enumerate(self.render._menu_rects):
                        if rect.collidepoint(mouse_pos):
                            self.pause_selected = i
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1 and hasattr(self.render, '_menu_rects'):
                    mouse_pos = ev.pos
                    for i, rect in enumerate(self.render._menu_rects):
                        if rect.collidepoint(mouse_pos):
                            self.pause_selected = i
                            if self.pause_selected == 0:
                                self.app_state = "PLAYING"
                            else:
                                self.app_state = "MENU"

        self.render.draw_pause_menu(self.pause_selected)
        self.render.render_frame()

    def _run_name_input_screen(self) -> None:
        """Manages text input for highscore submission."""
        is_victory = self.game_state.state == State.VICTORY

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.VIDEORESIZE:
                self.render.resize(ev.w, ev.h)
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    self.highscores.add_score(
                        self.input_name, self.game_state.score
                    )
                    self.app_state = "MENU"
                    return
                elif ev.key == pygame.K_BACKSPACE:
                    self.input_name = self.input_name[:-1]
                elif ev.unicode.isalnum() or ev.unicode == " ":
                    if len(self.input_name) < 10:
                        self.input_name += ev.unicode

        self.render.draw_name_input(
            self.input_name, self.game_state.score, is_victory
        )
        self.render.render_frame()

    def _run_highscore_screen(self) -> None:
        """Draw Highscore leaderboard."""
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.VIDEORESIZE:
                self.render.resize(ev.w, ev.h)
            elif ev.type == pygame.KEYDOWN:
                self.app_state = "MENU"

        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 36)
        title = font.render("TOP 10 SCORES (Press any key to return)", True, (255, 255, 0))
        self.screen.blit(title, (50, 50))

        for i, hs in enumerate(self.highscores.scores):
            entry = font.render(f"{i+1}. {hs['name']} - {hs['score']}", True, (255, 255, 255))
            self.screen.blit(entry, (100, 100 + (i * 35)))

        pygame.display.flip()


if __name__ == "__main__":
    app = Application()
    app.run()
