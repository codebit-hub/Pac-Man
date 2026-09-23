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
            scatter_target: tuple[int, int],
            speed: float
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

        self.speed = speed
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

    def reverse_direction(self) -> None:
        """Reverses ghost direction"""

        if self.current_dir != Direction.NONE:
            self.current_dir = self._get_opposite_dir(self.current_dir)

    def get_target_tile(
            self,
            pacman_x: int,
            pacman_y: int,
            pacman_dir: Direction,
            blinky_x: int = 0,
            blinky_y: int = 0
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
            pacman_dir: Direction,
            blinky_x: int = 0,
            blinky_y: int = 0
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
        time_per_tile = 1.0 / self.speed
        moved = False

        while self.move_timer >= time_per_tile:
            self.move_timer -= time_per_tile
            self._move(
                grid, pacman_x, pacman_y, pacman_dir, blinky_x, blinky_y
            )
            moved = True

        return moved

    def _move(
            self,
            grid: list[list[int]],
            pacman_x: int,
            pacman_y: int,
            pacman_dir: Direction,
            blinky_x: int = 0,
            blinky_y: int = 0
    ) -> None:
        """Determine best next valid target tile and moves"""

        if self.state == GhostState.CHASE:
            tx, ty = self.get_target_tile(
                pacman_x, pacman_y, pacman_dir, blinky_x, blinky_y)
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

    def __init__(
            self, spawn_x: int, spawn_y: int, speed: float) -> None:
        """Init Blinky in its top-right scatter corner"""

        # super() grants access to all parent properties and methods
        # scatter target is off the grid; Blinky will hug that corner
        super().__init__(
            "Red", spawn_x, spawn_y, scatter_target=(99, -1), speed=speed)

    def get_target_tile(
            self,
            pacman_x: int,
            pacman_y: int,
            pacman_dir: Direction,
            blinky_x: int = 0,
            blinky_y: int = 0
    ) -> tuple[int, int]:
        """Blinky's target is pacman's target cell"""

        return (pacman_x, pacman_y)


class Pinky(Ghost):
    """Pinky Ghost: Ambush logic, targeting 4 tiles ahead of Pac-Man."""

    def __init__(self, spawn_x: int, spawn_y: int, speed: float) -> None:
        """Init Pinky in top-left corner"""

        # Scatter target cell is off the grid to top-left
        super().__init__(
            "Pink", spawn_x, spawn_y, scatter_target=(-1, -1), speed=speed)

    def get_target_tile(
            self,
            pacman_x: int,
            pacman_y: int,
            pacman_dir: Direction,
            blinky_x: int = 0,
            blinky_y: int = 0
    ) -> tuple[int, int]:
        """Pinky targets 4 tiles ahead of Pacman's current direction."""

        # If Pacman has not moved, target his current direction
        if pacman_dir == Direction.NONE:
            return (pacman_x, pacman_y)

        dx, dy = pacman_dir.value

        # Multiply Pacman's direction vector by 4
        # to project the target forward by 4 cells
        target_x = pacman_x + (dx * 4)
        target_y = pacman_y + (dy * 4)

        return (target_x, target_y)


class Inky(Ghost):
    """Targets a reflection of Pacman relative to Blinky"""

    def __init__(self, spawn_x: int, spawn_y: int, speed: float) -> None:
        """Init Inky in bottom-right scatter corner"""

        super().__init__(
            "Cyan", spawn_x, spawn_y, scatter_target=(99, 99), speed=speed
        )

    def get_target_tile(
            self,
            pacman_x: int,
            pacman_y: int,
            pacman_dir: Direction,
            blinky_x: int = 0,
            blinky_y: int = 0
    ) -> tuple[int, int]:
        """Calculate target using Blinky's pos and Pac-Man's trajectory."""

        # Find the pivot point (2 tiles before Pacman)
        if pacman_dir == Direction.NONE:
            pivot_x = pacman_x
            pivot_y = pacman_y
        else:
            dx, dy = pacman_dir.value
            pivot_x = pacman_x + (dx * 2)
            pivot_y = pacman_y + (dy * 2)

        # Distance vector from Blinky to pivot point
        vector_x = pivot_x - blinky_x
        vector_y = pivot_y - blinky_y

        # Double the vector to find Inky's final target
        target_x = blinky_x + (vector_x * 2)
        target_y = blinky_y + (vector_y * 2)

        return (target_x, target_y)


class Clyde(Ghost):
    """Chases when far, retreats when close"""

    def __init__(self, spawn_x: int, spawn_y: int, speed: float) -> None:
        """Init Clyde with his bottom-left scatter corner."""
        super().__init__(
            "Orange", spawn_x, spawn_y, scatter_target=(-1, 99), speed=speed
        )

    def get_target_tile(
        self,
        pacman_x: int,
        pacman_y: int,
        pacman_dir: Direction,
        blinky_x: int = 0,
        blinky_y: int = 0
    ) -> tuple[int, int]:
        """Switch target based on distance to Pac-Man."""

        # Calculate Manhattan distance from Clyde to Pac-Man
        dist = self._manhattan_distance(
            self.grid_x, self.grid_y, pacman_x, pacman_y
        )

        if dist > 8:
            return (pacman_x, pacman_y)
        else:
            return self.scatter_target


if __name__ == "__main__":
    sys.path.append(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    )

    from src.maze_loader import MazeLoader
    from src.player import Player

    print("[*] Generating Ghost test environment...")

    # Generate the maze
    loader = MazeLoader()
    success = loader.generate(width=17, height=15, seed=42, pacgum_count=42)

    # Extract the generated maze and init pacman
    grid = loader.get_grid()
    pacman = Player(loader.spawn_point[0], loader.spawn_point[1])

    # Spawn Blinky in the top-right corner
    blinky = Blinky(len(grid[0]) - 2, 1, speed=4.5)
    pinky = Pinky(1, 1, speed=4.5)
    inky = Inky(len(grid[0]) - 2, len(grid) - 2, speed=4.5)
    clyde = Clyde(1, len(grid) - 2, speed=4.5)

    blinky.state = GhostState.CHASE
    pinky.state = GhostState.CHASE
    inky.state = GhostState.CHASE
    clyde.state = GhostState.CHASE

    controls = {'w': Direction.UP,
                's': Direction.DOWN,
                'a': Direction.LEFT,
                'd': Direction.RIGHT
                }

    action_log = "Press W/A/S/D to move, K to kill ghosts, Q to quit."

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
                elif x == pinky.grid_x and y == pinky.grid_y:
                    visual_row += "P"
                elif x == inky.grid_x and y == inky.grid_y:
                    visual_row += "I"
                elif x == clyde.grid_x and y == clyde.grid_y:
                    visual_row += "C"
                elif cell == 0:
                    visual_row += "#"
                elif cell == 4:
                    visual_row += "4"
                else:
                    visual_row += " "
            print(visual_row)

        print("-" * 35)
        print(f"Pac-Man: ({pacman.grid_x}, {pacman.grid_y})")

        bx, by = blinky.get_target_tile(
            pacman.grid_x, pacman.grid_y, pacman.current_dir,
            blinky.grid_x, blinky.grid_y)
        print(f"Blinky:  ({blinky.grid_x}, {blinky.grid_y}) | "
              f"Target: ({bx}, {by})")

        px, py = pinky.get_target_tile(
            pacman.grid_x, pacman.grid_y, pacman.current_dir,
            blinky.grid_x, blinky.grid_y)
        print(f"Pinky:   ({pinky.grid_x}, {pinky.grid_y}) | "
              f"Target: ({px}, {py})")

        ix, iy = inky.get_target_tile(
            pacman.grid_x, pacman.grid_y, pacman.current_dir,
            blinky.grid_x, blinky.grid_y)
        print(f"Inky:   ({inky.grid_x}, {inky.grid_y}) | "
              f"Target: ({ix}, {iy})")

        cx, cy = clyde.get_target_tile(
            pacman.grid_x, pacman.grid_y, pacman.current_dir,
            blinky.grid_x, blinky.grid_y)
        print(f"Clyde:   ({clyde.grid_x}, {clyde.grid_y}) | "
              f"arget: ({cx}, {cy})")

        print("-" * 35)

        if blinky.state == GhostState.EATEN:
            print(f"Respawn in: {blinky.respawn_timer:.1f}s")
        print(f"Log: {action_log}")

        if pinky.state == GhostState.EATEN:
            print(f"Respawn in: {pinky.respawn_timer:.1f}s")
        print(f"Log: {action_log}")

        if inky.state == GhostState.EATEN:
            print(f"Respawn in: {inky.respawn_timer:.1f}s")
        print(f"Log: {action_log}")

        if clyde.state == GhostState.EATEN:
            print(f"Respawn in: {clyde.respawn_timer:.1f}s")
        print(f"Log: {action_log}")

        print("-" * 35)

        # if pacman.grid_x == blinky.grid_x and pacman.grid_y == blinky.grid_y:
        #    print("GAME OVER! Blinky caught you!")
        #   break

        user_input = input("Action: ").strip().lower()
        if user_input == 'q':
            break
        elif user_input == 'r':
            pacman.respawn()
            action_log = "Player respawned at center."
            continue
        elif user_input == 'k':
            blinky.die()
            pinky.die()
            inky.die()
            clyde.die()
            action_log = "Blinky killed! Waiting for respawn..."
            action_log = "Pinky killed! Waiting for respawn..."
            action_log = "Inky killed! Waiting for respawn..."
            action_log = "Clyde killed! Waiting for respawn..."
        elif user_input in controls:
            new_dir = controls[user_input]
            pacman.set_direction(new_dir)
            action_log = f"Queued {new_dir.name}."

        # Store positions BEFORE they move to catch cross-overs
        prev_pac_x, prev_pac_y = pacman.grid_x, pacman.grid_y
        prev_bli_x, prev_bli_y = blinky.grid_x, blinky.grid_y
        prev_pin_x, prev_pin_y = pinky.grid_x, pinky.grid_y
        prev_ink_x, prev_ink_y = inky.grid_x, inky.grid_y
        prev_cly_x, prev_cly_y = clyde.grid_x, clyde.grid_y

        pacman.update(0.2, grid)
        blinky.update(
            0.2, grid, pacman.grid_x, pacman.grid_y, pacman.current_dir,
            blinky.grid_x, blinky.grid_y
        )
        pinky.update(
            0.2, grid, pacman.grid_x, pacman.grid_y, pacman.current_dir,
            blinky.grid_x, blinky.grid_y
        )
        inky.update(
            0.2, grid, pacman.grid_x, pacman.grid_y, pacman.current_dir,
            blinky.grid_x, blinky.grid_y
        )
        clyde.update(
            0.2, grid, pacman.grid_x, pacman.grid_y, pacman.current_dir,
            blinky.grid_x, blinky.grid_y
        )

        # Exact tile collisionn
        if pacman.grid_x == blinky.grid_x and pacman.grid_y == blinky.grid_y:
            print("GAME OVER! Blinky caught you!")
            break

        if pacman.grid_x == pinky.grid_x and pacman.grid_y == pinky.grid_y:
            print("GAME OVER! Pinky caught you!")
            break

        if pacman.grid_x == inky.grid_x and pacman.grid_y == inky.grid_y:
            print("GAME OVER! Inky caught you!")
            break

        if pacman.grid_x == clyde.grid_x and pacman.grid_y == clyde.grid_y:
            print("GAME OVER! Clyde caught you!")
            break

        # Cross-over collision (phasing check)
        blinky_cross = (
            pacman.grid_x == prev_bli_x
            and pacman.grid_y == prev_bli_y
            and blinky.grid_x == prev_pac_x
            and blinky.grid_y == prev_pac_y
        )
        if blinky_cross:
            print("GAME OVER! You collided head-on with Blinky!")
            break

        pinky_cross = (
            pacman.grid_x == prev_pin_x
            and pacman.grid_y == prev_pin_y
            and pinky.grid_x == prev_pac_x
            and pinky.grid_y == prev_pac_y
        )
        if pinky_cross:
            print("GAME OVER! You collided head-on with Pinky!")
            break

        inky_cross = (
            pacman.grid_x == prev_ink_x
            and pacman.grid_y == prev_ink_y
            and inky.grid_x == prev_pac_x
            and inky.grid_y == prev_pac_y
        )
        if inky_cross:
            print("GAME OVER! You collided head-on with Inky!")
            break

        clyde_cross = (
            pacman.grid_x == prev_cly_x
            and pacman.grid_y == prev_cly_y
            and clyde.grid_x == prev_pac_x
            and clyde.grid_y == prev_pac_y
        )
        if clyde_cross:
            print("GAME OVER! You collided head-on with Clyde!")
            break
