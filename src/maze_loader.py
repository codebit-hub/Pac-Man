import random
from typing import Any


class MazeLoader:
    """Wraps external maze generator, converts bitmasks into game grid"""

    def __init__(self) -> None:
        """Init the loader"""

        self.grid: list[list[int]] = []
        self.spawn_point: tuple[int, int] = (1, 1)

    def generate(
            self, width: int, height: int, seed: int, pacgum_count: int
    ) -> bool:
        """Generates maze from external package"""

        # Attempt import with fallback
        try:
            from mazegenerator import MazeGenerator

        except ImportError:
            print("Warning: 'mazegenerator' package is not installed.")
            return False

        # Load maze
        try:
            maze_gen = MazeGenerator(
                size=(width, height),
                perfect=False,
                entry_cell=(1, 1),
                exit_cell=(width - 1, height -1),
                seed=seed
            )

            # raw_maze receives all level bitmask rows lists
            raw_maze = maze_gen.maze

            self._convert_to_pacman_grid(raw_maze, width, height)
            self._place_super_pacgums(width, height)
            self._place_pacgums(seed, pacgum_count)
            self._calculate_spawn_point((width * 2) + 1, (height * 2) + 1)

            return True

        except Exception as err:
            print(f"Warning: Maze generation failed: {err}")
            return False

    def _convert_to_pacman_grid(
            self, raw_maze: list[list[int]], width: int, height: int
    ) -> None:
        """Convert a bitmask maze into a 2D tile grid.
        Bitmasks: 1=North, 2=East, 4=South, 8=West.
        Grid value: 0=Wall, 1=Empty, 2=Pacgum, 3=Super-Pacgum.
        """
        # [][][][][][]
        # [][A][-][B][]
        # [][][][][][]

        grid_w = (width * 2) + 1
        grid_h = (height * 2) + 1

        # Init the grid with 0
        self.grid = []
        for _ in range(grid_h):
            row = [0] * grid_w
            self.grid.append(row)

        # Build the grid
        for y in range(height):
            for x in range(width):
                cell = raw_maze[y][x]

                # Calculate center in grid
                gx = (x * 2) + 1
                gy = (y * 2) + 1

                # '42'
                if cell == 15:
                    self.grid[gy][gx] = 4

                    # Set out '42' blocks
                    if x < width - 1 and raw_maze[y][x + 1] == 15:
                        self.grid[gy][gx + 1] = 4
                    if y < height - 1 and raw_maze[y + 1][x] == 15:
                        self.grid[gy + 1][gx] = 4

                    # Fill diagonal inner corners for visual solidity
                    if x < width - 1 and y < height - 1:
                        if (raw_maze[y][x + 1] == 15 and
                            raw_maze[y + 1][x] == 15):
                            self.grid[gy + 1][gx + 1] = 4
                    continue

                # Empty the center of the grid
                self.grid[gy][gx] = 1

                # If East is open, open West of next cell
                # 9 (1001) & 2 (0010)
                if not (cell & 2):
                    self.grid[gy][gx + 1] = 1

                # If South open, open North of cell below
                # 9 (1001) & 4 (0100)
                if not (cell & 4):
                    self.grid[gy + 1][gx] = 1

    def _place_super_pacgums(self, width: int, height: int) -> None:
        """Places power pellets in 4 maze corners"""

        grid_w = (width * 2) + 1
        grid_h = (height * 2) + 1

        corners = [
            (1, 1),
            (grid_w - 2, 1),
            (1, grid_h - 2),
            (grid_w - 2, grid_h -2)
        ]

        for cx, cy in corners:
            # Only place if it is an empty corridor
            if self.grid[cy][cx] == 1:
                self.grid[cy][cx] = 3

    def _place_pacgums(self,seed: int, max_pacgums: int) -> None:
        """Randomly distributes set pacgums in empty corridors"""

        # Find empty corridors
        empty_corridors = []
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if self.grid[y][x] == 1:
                    empty_corridors.append((x, y))

        # Use same seed to ensure reproducibility for level 1
        random.seed(seed)

        # Limit pacgums to empty spaces
        amount_to_place = min(max_pacgums, len(empty_corridors))

        # Safe fallback for too many pacgums over empty corridors
        if max_pacgums > len(empty_corridors):
            print(f"Warning: Requested {max_pacgums} pacgums, but only "
                  f"{len(empty_corridors)} spaces available. Clamping.")

        # Select random coords from empty spaces
        chosen_spots = random.sample(empty_corridors, amount_to_place)

        # Place pacgums
        for x, y in chosen_spots:
            self.grid[y][x] = 2

    def _calculate_spawn_point(self, grid_w: int, grid_h: int) -> None:
        """Find the nearest valid empty tile to the center of the maze."""
        center_x = grid_w // 2
        center_y = grid_h // 2

        queue = [(center_x, center_y)]
        visited = set([(center_x, center_y)])

        while queue:
            cx, cy = queue.pop(0)

            # If we found an empty corridor or a pacgum tile
            if self.grid[cy][cx] in (1, 2, 3):
                self.spawn_point = (cx, cy)
                # Clear any pacgum at the spawn point
                if self.grid[cy][cx] == 2:
                    self.grid[cy][cx] = 1
                return

            # Check surrounding tiles (Up, Down, Left, Right)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx = cx + dx
                ny = cy + dy

                if 0 <= nx < grid_w and 0 <= ny < grid_h:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

    def get_grid(self) -> list[list[int]]:
        """Return converted pacman grid"""

        return self.grid


if __name__ == "__main__":
    print("[*] Testing MazeLoader...")

    loader = MazeLoader()

    success = loader.generate(
        width=17, height=25, seed=42, pacgum_count=42)

    if success:
        grid = loader.get_grid()
        grid_width = len(grid[0])
        grid_height = len(grid)
        print("[+] Maze successfully generated: "
              f"{grid_width} x {grid_height}.")

        # Display # - wall, . - pacgum, * - power pellet
        for y, row in enumerate(grid):
            visual_row = ""
            for x, cell in enumerate(row):
                if (x, y) == loader.spawn_point:
                    visual_row += "@"  # Spawn Point
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
    else:
        print("[-] Maze generation failed or package is missing.")
