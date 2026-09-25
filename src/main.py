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

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pac-Man")

        # Configurations & Highscores
        cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        self.config = ConfigManager()
        self.config.load(cfg_path)

        self.game_state = GameState(self.config)
        self.highscores = HighScoreManager(self.config.get("highscore_filename"))

        # Setup Vokotera's Menu and Monkey-Patch the selections
        self.menu = Menu(self.screen)
        self.app_state = "MENU"  # MENU, PLAYING, GAME_OVER, HIGHSCORES

        # Store the original menu activate method
        self._og_activate = self.menu._activate_item

        def custom_activate(index: int) -> None:
            if index == 0:
                self._start_new_game()
            elif index == 2:
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
        self.renderer = Render()
        self.renderer.setup_display(grid_w, grid_h)

        base = os.path.dirname(__file__)
        self.renderer.load_spritesheet(os.path.normpath(
            os.path.join(base, "..", "Sprites", "2-Sprites", "spritesheet.png")))
        self.renderer.load_dot(os.path.normpath(
            os.path.join(base, "..", "Sprites", "pacman-art", "other", "dot.png")))
        self.renderer.load_player_frames(os.path.normpath(
            os.path.join(base, "..", "Sprites", "pacman-art")))
        self.renderer.load_ghost_sprites()

        self.game_state.setup_level(self.config.get("pacgum"))

        # Reset wave timers
        self.is_scatter_wave = True
        self.wave_timer = 7.0
        self.was_frightened = False

    def _init_ghosts(self) -> None:
        """Spawn ghosts with optional randomization."""
        w, h = len(self.grid[0]), len(self.grid)
        locs = [(w - 2, 1), (3, 1), (w - 2, h - 2), (1, h - 2)]

        if self.config.get("ghost_behavior_random"):
            random.shuffle(locs)

        self.blinky = Blinky(locs[0][0], locs[0][1], speed=4.5)
        self.pinky = Pinky(locs[1][0], locs[1][1], speed=4.5)
        self.inky = Inky(locs[2][0], locs[2][1], speed=4.5)
        self.clyde = Clyde(locs[3][0], locs[3][1], speed=4.5)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]

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
                    self.menu.handle_event(ev)
                self.menu.draw_main_menu()
                pygame.display.flip()

            elif self.app_state == "PLAYING":
                self._run_game_frame(dt)

            elif self.app_state == "GAME_OVER":
                self._run_game_over_screen()

            elif self.app_state == "HIGHSCORES":
                self._run_highscore_screen()

    def _run_game_frame(self, dt: float) -> None:
        """Execute one frame of gameplay."""
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_w, pygame.K_UP):
                    self.player.set_direction(Direction.UP)
                elif ev.key in (pygame.K_s, pygame.K_DOWN):
                    self.player.set_direction(Direction.DOWN)
                elif ev.key in (pygame.K_a, pygame.K_LEFT):
                    self.player.set_direction(Direction.LEFT)
                elif ev.key in (pygame.K_d, pygame.K_RIGHT):
                    self.player.set_direction(Direction.RIGHT)
                elif ev.key == pygame.K_ESCAPE:
                    self.app_state = "MENU"
                    # Reset screen size for menu
                    self.screen = pygame.display.set_mode((800, 600))
                    return

        # 1. Update State
        self.game_state.update(dt)
        self._update_wave_timers(dt)

        # Check for Level Transition or Death BEFORE moving entities
        if self.game_state.state == State.LEVEL_TRANSITION:
            self._load_level()
            return
        elif self.game_state.state in (State.GAME_OVER, State.VICTORY):
            self.highscores.add_score("PLY", self.game_state.score)
            self.app_state = "GAME_OVER"
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
                        self.player.respawn()
                        self._init_ghosts()
                    return

        # 3. Draw Frame
        self.renderer.screen.fill((20, 20, 40))
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == 0:
                    self.renderer.draw_wall(x, y)
                elif cell == 4:
                    self.renderer.draw_wall(x, y, is_logo=True)
                elif cell == 2:
                    self.renderer.draw_pacgum(x, y)
                elif cell == 3:
                    self.renderer.draw_powergum(x, y)

        self.renderer.draw_player(
            self.player.grid_x, self.player.grid_y, self.player.current_dir, dt
        )
        for g in self.ghosts:
            self.renderer.draw_ghost(
                g.grid_x, g.grid_y, g.color_name, g.state.value, self.game_state.frigthened_timer
            )

        # Determine text for the current wave mode
        mode_text = "SCATTER" if self.is_scatter_wave else "CHASE"
        if self.game_state.is_frightened:
            mode_text = "FLEE"

        self.renderer.draw_hud(
            self.game_state.score,
            self.game_state.lives,
            self.game_state.time_remaining,
            self.game_state.current_level_idx + 1,
            mode_text
        )

        self.renderer.render_frame()

    def _run_game_over_screen(self) -> None:
        """Draw basic Game Over screen waiting for keypress."""
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.KEYDOWN:
                self.app_state = "MENU"
                self.screen = pygame.display.set_mode((800, 600))

        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)

        if self.game_state.state == State.VICTORY:
            msg = "VICTORY!"
            color = (0, 255, 0)  # Green
        else:
            msg = "GAME OVER"
            color = (255, 0, 0) # Red

        text = font.render(f"{msg} - Score: {self.game_state.score}", True, color)
        self.screen.blit(
            text,
            text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        )
        pygame.display.flip()

    def _run_highscore_screen(self) -> None:
        """Draw Highscore leaderboard."""
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
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
