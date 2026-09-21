import math
from enum import Enum
import os
import sys
# Use pacman's direction of movement cost
from player import Direction


# Ghost behaviour

class GhostState(Enum):
    """Four ghost states"""

    SCATTER = 1    # Circling their home corner
    CHASE = 2      # Actively pursuing Pac-Man
    FLEE = 3       # Frightened mode (vulnerable)
    EATEN = 4      # Get respawn


class Ghost:
    """Base class for general ghost movement"""

    def __init__(
            self,
            color_name: str,
            spawn_x: int,
            spawn_y: int,
            scatter_target: tuple[int, int]
    ) -> None:
        """Init core ghost properties"""

        self.color_name = color_name
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y

        self.grid_x = spawn_x
        self.grid_y = spawn_y
        self.current_dir = Direction.NONE

        self.state = GhostState.SCATTER
        self.scatter_target = scatter_target

        self.speed = 4.5
        self.move_timer = 0.0
        self.respawn_delay = 5.0
        self.respawn_timer = 0.0

    def die(self) -> None:
        """Triggers ghost eaten state and respawning"""

        # Change ghost state to Eaten and set timer
        self.state = GhostState.EATEN
        self.respawn_timer = self.respawn_delay

        # Move the ghost off the grid
        self.grid_x = -1
        self.grid_y = -1

    def get_target_tile(
            self, pacman_x: int, pacman_y: int, pacman_dir: Direction
    ) -> tuple[int, int]:
        """Calc the ghost's target tile. Overridden by child class"""

        return (0, 0)

    def _get_opposite_dir(self, direction: Direction) -> Direction:
        """Returns 180 opposite direction"""

        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
            Direction.NONE: Direction.NONE
        }
        return opposites[direction]

    def _manhattan_distance(
            self, x1: int, y1: int, x2: int, y2: int
    ) -> int:
        """Calculate grid-based distance btw 2 points"""

        return abs(x1 - x2) + abs(y1 - y2)

    def update(
            self,
            delta_time: float,
            grid: list[list[int]],
            pacman_x: int,
            pacman_y: int,
            pacman_dir: Direction
    ) -> bool:
        """Manages set timers and makes a move"""

        if self.state == GhostState.EATEN:
            self.respawn_timer -= delta_time
            if self.respawn_timer <= 0:
                # Timer is up, respawn ghost
                self.grid_x = self.spawn_x
                self.grid_y = self.spawn_y
                self.state = GhostState.CHASE
                self.current_dir = Direction.NONE
            return False

        self.move_timer += delta_time
        time_per_title = 1.0 / self.speed
        moved = False

        while self.move_timer >= time_per_title:
            self.move_timer -= time_per_title
            self._move(grid, pacman_x, pacman_y, pacman_dir)
            moved = True

        return moved

    def _move(
            self,
            grid: list[list[int]],
            pacman_x: int,
            pacman_y: int,
            pacman_dir: Direction
    ) -> None:
        """Determine best next valid target tile and moves"""

        if self.state == GhostState.CHASE:
            tx, ty = self.get_target_tile(pacman_x, pacman_y, pacman_dir)
        elif self.state == GhostState.SCATTER:
            tx, ty = self.scatter_target
        elif self.state == GhostState.FLEE:
            # When fleeing, ghost are targeting their spawn point
            tx, ty = self.spawn_x, self.spawn_y
        else:
            return

        candidates = [
            (Direction.UP, 0, -1),
            (Direction.LEFT, -1, 0),
            (Direction.DOWN, 0, 1),
            (Direction.RIGHT, 1, 0)
        ]

        best_dir = Direction.NONE
        shortest_dist = float('inf')
        opposite = self._get_opposite_dir(self.current_dir)

        for d, dx, dy in candidates:
            if d == opposite and self.current_dir != Direction.NONE:
                continue

            nx = self.grid_x + dx
            ny = self.grid_y + dy

            if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                if grid[ny][nx] not in (0, 4):
                    dist = self._manhattan_distance(nx, ny, tx, ty)

                    if dist < shortest_dist:
                        shortest_dist = dist
                        best_dir = d

        # && Dead-end ghost reversed movement
        if best_dir == Direction.NONE and self.current_dir != Direction.NONE:
            ox = self.grid_x + opposite.value[0]
            oy = self.grid_y + opposite.value[1]
            if 0 <= oy < len(grid) and 0 <= ox < len(grid[0]):
                if grid[oy][ox] not in (0, 4):
                    best_dir = opposite

        if best_dir != Direction.NONE:
            self.grid_x += best_dir.value[0]
            self.grid_y += best_dir.value[1]
            self.current_dir = best_dir


class Blinky(Ghost):
    """Red Ghost: Directly chases pacman's current tile."""

    def __init__(self, spawn_x: int, spawn_y: int) -> None:
        """Init Blinky in its top-right scatter corner"""

        # super() grants access to all parent properties and methods
        # scatter target is off the grid; Blinky will hug that corner
        super().__init__("Red", spawn_x, spawn_y, scatter_target=(99, -1))

    def get_target_tile(
            self, pacman_x, pacman_y, pacman_dir: Direction
            ) -> tuple[int, int]:
        """Blinky's target is pacman's target cell"""

        return (pacman_x, pacman_y)


if __name__ == "__main__":
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    )

    from src.maze_loader import MazeLoader
    from src.player import Player

    print("[*] Generating Ghost test environment...")
    print(f"os.path.dirname(__file__): {os.path.dirname(__file__)}")
    print(f"os.path.join(): {os.path.join(os.path.dirname(__file__), "..")}")
    print(f"os.path.abspath(): {os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))}")
    print(f"os.append: {sys.path.append(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))}")

    print("[*] Generating Ghost test environment...")

    # Generate the maze
    loader = MazeLoader()
    success = loader.generate(width=17, height=15, seed=42, pacgum_count=42)

    # Extract the generated maze and init pacman
    grid = loader.get_grid()
    pacman = Player(loader.spawn_point[0], loader.spawn_point[1])

    # Spawn Blinky in the top-right corner
    blinky = Blinky(len(grid[0]) - 2, 1)
    blinky.state = GhostState.CHASE

    controls = {'w': Direction.UP,
                's': Direction.DOWN,
                'a': Direction.LEFT,
                'd': Direction.RIGHT,
                'k': 'kill'}

    action_log = "Press W/A/S/D to move, K to kill Blinky, Q to quit."

    while True:
        # clear terminal
        print("\033[2J\033[H", end="", flush=True)

        for y, row in enumerate(grid):
            visual_row = ""
            for x, cell in enumerate(row):
                if x == pacman.grid_x and y == pacman.grid_y:
                    visual_row += "M"
                elif x == blinky.grid_x and y == blinky.grid_y:
                    visual_row += "B"
                elif cell == 0:
                    visual_row += "#"
                elif cell == 4:
                    visual_row += "C"
                else:
                    visual_row += " "
            print(visual_row)

        print("-" * 35)
        print(f"Pac-Man: ({pacman.grid_x}, {pacman.grid_y})")
        print(f"Blinky:  ({blinky.grid_x}, {blinky.grid_y}) | State: {blinky.state.name}")
        if blinky.state == GhostState.EATEN:
            print(f"Respawn in: {blinky.respawn_timer:.1f}s")
        print(f"Log: {action_log}")
        print("-" * 35)

        if pacman.grid_x == blinky.grid_x and pacman.grid_y == blinky.grid_y:
            print("GAME OVER! Blinky caught you!")
            break

        user_input = input("Action: ").strip().lower()
        if user_input == 'q':
            break
        elif user_input == 'k':
            blinky.die()
            action_log = "Blinky killed! Waiting for respawn..."
        elif user_input in controls:
            pacman.set_direction(controls[user_input])

        # Store positions BEFORE they move to catch cross-overs
        prev_pac_x, prev_pac_y = pacman.grid_x, pacman.grid_y
        prev_bli_x, prev_bli_y = blinky.grid_x, blinky.grid_y

        pacman.update(0.2, grid)
        blinky.update(
            0.2, grid, pacman.grid_x, pacman.grid_y, pacman.current_dir
        )

        # Exact tile collisionn
        if pacman.grid_x == blinky.grid_x and pacman.grid_y == blinky.grid_y:
            print("GAME OVER! Blinky caught you!")
            break

        # Cross-over collision (phasing check)
        if (pacman.grid_x == prev_bli_x and pacman.grid_y == prev_bli_y and
            blinky.grid_x == prev_pac_x and blinky.grid_y == prev_pac_y):
            print("GAME OVER! You collided head-on with Blinky!")
            break
