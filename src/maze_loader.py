from typing import Any


class MazeLoader:
    """Wraps external maze generator, converts bitmasks into game grid"""

    def __init__(self) -> None:
        """Init the loader"""

        self.grid: list[list[int]] = []

    def generate(self, width: int, height: int, seed: int) -> bool:
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

        grid_w = (width * 2) + 1
        grid_h = (height * 2) + 1

        # Init full wall grid
        self.grid = [[0 for _ in range(grid_w)] for _ in range(grid_h)]

        # Build the grid
        for y in range(height):
            for x in range(width):
                cell = raw_maze[y][x]
                gx = (x * 2) + 1
                gy = (y * 2) + 1

                # Center of cell is always corridor with pacgum
                self.grid[gy][gx] = 2

                # East connection bit 2
                if cell & 2:
                    self.grid[gy][gx + 1] = 2

                # South connection bit 4
                if cell & 4:
                    self.grid[gy + 1][gx] = 2

        self._place_super_pacgums(grid_w, grid_h)

    def _place_super_pacgums(self, grid_w: int, grid_h: int) -> None:
        """Places power pellets in 4 maze corners"""

        corners = [
            (1, 1),
            (grid_w - 2, 1),
            (1, grid_h - 2),
            (grid_w - 2, grid_h -2)
        ]

        for cx, cy in corners:
            # Check the corner is open
            if self.grid[cy][cx] in (1, 2):
                self.grid[cy][cx] = 3

    def get_grid(self) -> list[list[int]]:
        """Return converted pacman grid"""

        return self.grid


if __name__ == "__main__":
    print("[*] Testing MazeLoader...")

    loader = MazeLoader()

    success = loader.generate(width=21, height=21, seed=42)

    if success:
        grid = loader.get_grid()
        print(f"[+] Maze successfully generated: {len(grid[0])} x {len(grid)}.")

        # Display # - wall, . - pacgum, * - power pellet
        for row in grid:
            visual = "".join(
                "#" if c == 0 else " " if c == 1 else "." if c == 2 else "*"
                for c in row
            )
            print(visual)

        for row in grid:
            line = []
            for c in row:
                if c == 0:
                    line.append('#')
                elif c == 1:
                    line.append('.')
                elif c == 2:
                    line.append('*')
                else:
                    line.append(' ')
            output_row = "".join(line)
            print(output_row)
    else:
        print("[-] Maze generation failed or package is missing.")
