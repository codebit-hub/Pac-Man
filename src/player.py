from enum import Enum


class Direction(Enum):
    """Enumeration of possible pacman movement direction"""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)


class Player:
    """Defines Pacman in the game grid"""

    def __init__(self, spawn_x: int, spawn_y: int) -> None:
        """Initializes pacman at spawn cell"""

        self.spawn_x: int = spawn_x
        self.spawn_y: int = spawn_y

        # Logical position in the maze grid
        self.grid_x: int = spawn_x
        self.grid_y: int = spawn_y

        # Movement directions
        self.current_dir: Direction = Direction.NONE
        self.next_dir: Direction = Direction.NONE

        # Speed control (5.0 -> 5 tiles per second)
        self.speed: float = 5.0
        self.move_timer: float = 0.0

    def respawn(self) -> None:
        """Reset Pacman to spawn position"""

        self.grid_x = self.spawn_x
        self.grid_y = self.spawn_y
        self.current_dir = Direction.NONE
        self.next_dir = Direction.NONE
        self.move_timer = 0.0

    def set_direction(self, direction: Direction) -> None:
        """Queue next intended direction from player input"""

        self.next_dir = direction

    def _is_walkable(self, grid: list[list[int]], x: int, y: int) -> bool:
        """Checks if a specific grid cell is walkable"""

        # Walkable tiles: 1 (Empty), 2 (Pacgum), and 3 (Super-Pacgum).
        # Blocked titles: 0 (Walls), 4 (Logo Walls).

        # Prevent out-of-bound errors (off-the-map error)
        if y < 0 or y >= len(grid):
            return False
        if x < 0 or x >= len(grid[0]):
            return False

        tile_value = grid[y][x]

        if tile_value in (1, 2, 3):
            return True

        return False

    def update(self, delta_time: float, grid: list[list[int]]) -> bool:
        """Moves pacman based on delta time passing and grid position"""

        # delta_time - time passed since the last frame
        # at frame rate of 60 fps, delta time increments at 0,016 sec
        # (1/60 = 0.0166 sec). self.speed = 5, 5 tiles/sec
        # speed per tile = 1/5 = 0.2 sec
        # pacman moves as soon as timer reaches 0.2
        # pacman's speed is tighted to timer, not frame rate
        # high or slow frame rates would have modifed speed
        # timer makes the speed tighted to time - same on all pc

        # Returns True, if pacman moved, False otherwise

        self.move_timer += delta_time

        # Calculate time required to cross 1 tile
        time_per_tile = 1.0 / self.speed

        if self.move_timer >= time_per_tile:
            # Enough time accumulated to move
            # subtract this time and move
            self.move_timer -= time_per_tile
            return self._attempt_move(grid)

        return False

    def _attempt_move(self, grid: list[list[int]]) -> bool:
        """Attempts to move pacman in current direction"""

        # 1. Pacman tries to move in next direction if walkable
        # 2. Pacman tries to move in current direction
        # 3. Else, pacman stops

        # 1. Tries to move in the queued direction first
        next_dx, next_dy = self.next_dir.value
        target_x = self.grid_x + next_dx
        target_y = self.grid_y + next_dy

        if self.next_dir != Direction.NONE:
            if self._is_walkable(grid, target_x, target_y):
                # If True, turn is valid, go there
                self.grid_x = target_x
                self.grid_y = target_y
                # hands off the move, changes current_dir
                self.current_dir = self.next_dir
                return True

        # 2. If pacman can't turn, he tries going straight
        curr_dx, curr_dy = self.current_dir.value
        straight_x = self.grid_x + curr_dx
        straight_y = self.grid_y + curr_dy

        if self.current_dir != Direction.NONE:
            if self._is_walkable(grid, straight_x, straight_y):
                # If True, continue straight
                self.grid_x = straight_x
                self.grid_y = straight_y
                return True
            else:
                # If False, pacman move is blocked, stop.
                self.current_dir = Direction.NONE

        return False


if __name__ == "__main__":
    import os
    import sys

    # import maze loader from game root/ or src/
    # importing maze loader path for running from root
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

    from src.maze_loader import MazeLoader

    # Creating testing environment
    loader = MazeLoader()
    success = loader.generate(
        width=17, height=25, seed=42, pacgum_count=42
    )

    if not success:
        print("[-] Maze generation failed. Check maze_loader.py")
        sys.exit(1)

    grid = loader.get_grid()

    # pacman = Player(loader.spawn_point[0], loader.spawn_point[1])
    spawn_x, spawn_y = loader.spawn_point
    pacman = Player(spawn_x, spawn_y)

    # Map keyboard inputs to Directions enums
    controls = {
        'w': Direction.UP,
        's': Direction.DOWN,
        'a': Direction.LEFT,
        'd': Direction.RIGHT
    }
    action_log = ("Game started. Press W/A/S/D to queue direction, \n"
                  "R to respawn, Q to quit.")

    def clear_terminal() -> None:
        """Clear the terminal window w/o invoking a shell os.system command"""

        print("\033[2J\033[H", end="", flush=True)
        # This is an ANSI escape sequence sent to the terminal:
        # \033 = ESC character (ASCII 27)
        # [2J = clear the screen
        # [H = move cursor to the home position (top-left)
        # redraws the terminal from the top

    while True:
        # Clear terminal for continous redrawing
        # os.system('cls' if os.name == 'nt' else 'clear')
        clear_terminal()

        # 1. Draw the maze and pacman
        # Display grid
        for y, row in enumerate(grid):
            visual_row = ""
            for x, cell in enumerate(row):
                # if (x, y) == loader.spawn_point:
                #    visual_row += "@"  # Spawn Point
                if x == pacman.grid_x and y == pacman.grid_y:
                    visual_row += "M"  # Pacman
                elif cell == 0:
                    visual_row += "#"  # Wall
                elif cell == 4:
                    visual_row += "L"  # Logo Wall (The '42')
                elif cell == 1:
                    visual_row += " "  # Empty Corridor
                elif cell == 2:
                    visual_row += "."  # Pacgum
                elif cell == 3:
                    visual_row += "P"  # Super-Pacgum
            print(visual_row)

        # 2. Display HUD and Logs
        print("-" * 35)
        print(f"Current Dir: {pacman.current_dir.name} | "
              f"Queued Dir: {pacman.next_dir.name}")
        print(f"Position: ({pacman.grid_x}, {pacman.grid_y})")
        print(f"Log: {action_log}")
        print("-" * 35)

        # 3. Ger User Input
        user_input = input("Enter action (w/a/s/d/r/q): ").strip().lower()

        if user_input == 'q':
            break
        elif user_input == 'r':
            pacman.respawn()
            action_log = "Player respawned at center."
            continue
        elif user_input in controls:
            new_dir = controls[user_input]
            pacman.set_direction(new_dir)
            action_log = f"Queued {new_dir.name}."
        else:
            # Just pressing Enter
            action_log = "Waiting for key..."

        # 4. Simulate time passinng (set time intervals for crossing 1 tile)
        time_to_pass = 1.0 / pacman.speed
        moved = pacman.update(time_to_pass, grid)

        if moved:
            action_log += f" Moved to ({pacman.grid_x}, {pacman.grid_y})."
        else:
            action_log += " Blocked by wall."
