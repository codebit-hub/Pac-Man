import os
import sys
import pygame
import time

from maze_loader import MazeLoader
from player import Player, Direction
from ghost import GhostState, Blinky, Pinky, Inky, Clyde
from renderer import Render


class GameEngine:
    """Central game controller"""

    def __init__(self) -> None:
        """Init game components and global timers"""

        self.loader = MazeLoader()
        self.loader.generate(width=17, height=25, seed=42, pacgum_count=42)
        self.grid = self.loader.get_grid()

        # Init entities
        spawn_x, spawn_y = self.loader.spawn_point
        self.player = Player(spawn_x, spawn_y)

        grid_w = len(self.grid[0])
        grid_h = len(self.grid)

        # Spawn ghost in corners
        self.blinky = Blinky(grid_w - 2, 1, speed=4.5)
        self.pinky = Pinky(1, 1, speed=4.5)
        self.inky = Inky(grid_w - 2, grid_h - 2, speed=4.5)
        self.clyde = Clyde(1, grid_h - 2, speed=4.5)
        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]

        # Global wave Scatter/Chase timers
        self.is_scatter_wave = True
        self.wave_timer = 7.0   # 7 sec of scatter

        # Flee mode (after eating pellet)
        self.is_frightened = False
        self.frightened_timer = 0.0

        # Game stats
        self.score = 0
        self.lives = 3
        self.running = True

        # Setup Frontend
        self.renderer = Render()
        self.renderer.setup_display(grid_w, grid_h)

        # Reach graphics entities
        base_dir = os.path.dirname(__file__)
        dot_path = os.path.normpath(os.path.join(base_dir, "..", "Assets", "pacman", "other", "dot.png"))
        player_path = os.path.normpath(os.path.join(base_dir, "..", "Assets", "pacman"))

        self.renderer.load_dot(dot_path)
        self.renderer.load_player_frames(player_path)
        self.renderer.load_ghost_assets()

    def _update_wave_timers(self, delta_time: float) -> None:
        """Manages global switching Scatter/Chase"""

        if self.is_frightened:
            self.frightened_timer -= delta_time
            if self.frightened_timer <= 0:
                self.is_frightened = False
                # Restore previous wave state
                if self.is_scatter_wave:
                    target_state = GhostState.SCATTER
                else:
                    target_state = GhostState.CHASE

                for ghost in self.ghosts:
                    if ghost.state != GhostState.EATEN:
                        ghost.state = target_state
            return

        self.wave_timer -= delta_time
        if self.wave_timer <= 0:
            # Flip the timer
            self.is_scatter_wave = not self.is_scatter_wave

            if self.is_scatter_wave:
                self.wave_timer = 7.0  # 7 sec of scatter
                target_state = GhostState.SCATTER
            else:
                self.wave_timer = 20.0  # 20 sec of chase
                target_state = GhostState.CHASE

            # Apply new state and force reverse ghost mode
            for ghost in self.ghosts:
                if ghost.state != GhostState.EATEN:
                    ghost.state = target_state
                    ghost.reverse_direction()

    def _check_dot_consumption(self) -> None:
        """Handle eating pacgums and power pellets."""
        px, py = self.player.grid_x, self.player.grid_y
        cell_value = self.grid[py][px]

        if cell_value == 2:   # pacgum
            self.grid[py][px] = 1  # becomes empty
            self.score += 10
        elif cell_value == 3:  # pellet
            self.grid[py][px] = 1
            self.score += 50
            self._trigger_frightened_mode()

    def _trigger_frightened_mode(self) -> None:
        """Switch ghosts to Flee mode"""

        self.is_frightened = True
        self.frightened_timer = 7.0  # 7 seconds of vulnerability

        for ghost in self.ghosts:
            if ghost.state != GhostState.EATEN:
                ghost.state = GhostState.FLEE
                ghost.reverse_direction()

    def _check_collisions(self) -> None:
        """Detect intersections between Pacman and ghosts"""

        px, py = self.player.grid_x, self.player.grid_y

        for ghost in self.ghosts:
            # Exact tile collision
            if px == ghost.grid_x and py == ghost.grid_y:
                self._resolve_collision(ghost)

    def _resolve_collision(self, ghost) -> None:
        """Determines outcome based on ghost state"""

        # Pacman eats a ghost
        if ghost.state == GhostState.FLEE:
            ghost.die()
            self.score += 200
            print(f"Ghost Eaten! Score: {self.score}")
        # Ghost eats Pacman
        elif ghost.state in (GhostState.CHASE, GhostState.SCATTER):
            self.lives -= 1
            print(f"Pac-Man died! Lives remaining: {self.lives}")
            if self.lives <= 0:
                print("GAME OVER")
                self.running = False
            else:
                self._reset_positions()

    def _reset_positions(self) -> None:
        """Return all entities to their starting tiles after death"""

        self.player.respawn()

        grid_w = len(self.grid[0])
        grid_h = len(self.grid)

        # Reset ghost positions and states
        self.blinky.grid_x, self.blinky.grid_y = grid_w - 2, 1
        self.pinky.grid_x, self.pinky.grid_y = 1, 1
        self.inky.grid_x, self.inky.grid_y = grid_w - 2, grid_h - 2
        self.clyde.grid_x, self.clyde.grid_y = 1, grid_h - 2

        for ghost in self.ghosts:
            ghost.state = GhostState.SCATTER
            ghost.current_dir = Direction.NONE

        self.is_scatter_wave = True
        self.wave_timer = 7.0
        self.is_frightened = False

    def run(self) -> None:
        """Main game loop"""

        last_time = time.perf_counter()

        while self.running:
            # delta_time = clock.tick(60) / 1000.0
            current_time = time.perf_counter()
            delta_time = current_time - last_time

            # Cap framerate to about 60 FPS
            if delta_time < (1.0 / 60.0):
                time.sleep((1.0 / 60.0) - delta_time)
                current_time = time.perf_counter()
                delta_time = current_time - last_time

            last_time = current_time
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.player.set_direction(Direction.UP)
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.player.set_direction(Direction.DOWN)
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        self.player.set_direction(Direction.LEFT)
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        self.player.set_direction(Direction.RIGHT)
                if event.type == pygame.VIDEORESIZE:
                    window_w, window_h = event.w, event.h
                    self.renderer.resize(window_w, window_h)

            # Update backend
            self._update_wave_timers(delta_time)
            self.player.update(delta_time, self.grid)

            for ghost in self.ghosts:
                ghost.update(
                    delta_time, self.grid,
                    self.player.grid_x, self.player.grid_y,
                    self.player.current_dir,
                    self.blinky.grid_x, self.blinky.grid_y
                )
            self._check_dot_consumption()
            self._check_collisions()

            # Draw frontend
            self.renderer.screen.fill((20, 20, 40))

            # Draw map
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

            # Draw entities
            self.renderer.draw_player(
                self.player.grid_x, self.player.grid_y,
                self.player.current_dir, delta_time
            )

            # Note: Vokotera will need to add a `draw_ghost()` method to renderer
            # For now, we rely on the grid and Pac-Man rendering to test the loop.

            self.renderer.render_frame()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GameEngine()
    game.run()
