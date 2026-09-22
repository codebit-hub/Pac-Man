from os import environ
import pygame
import os
import math
from typing import Optional, cast
from maze_loader import MazeLoader
from player import Player, Direction

class Render:
    def __init__(self, max_width: int = 1280, max_heigth: int = 960) -> None:
        """Initialize the renderer with safe max window bounds."""
        pygame.init()
        self.max_w = max_width
        self.max_h = max_heigth
        self.title_size: int = 16
        self.sheet = None
        self.dot_img: Optional[pygame.Surface] = None
        self._powergum_tick: int = 0
        self.player_frames: dict = {}
        self.anim_frame: int = 0
        self.anim_timer: float = 0.0
        self.ANIM_SPEED: float = 0.1  # seconds per frame
        self.last_dir: Direction = Direction.RIGHT  # fallback facing direction

    def setup_display(self, grid_w: int, grid_h: int) -> None:
        """Calculate tile size and create the Pygame window."""
        title_w = self.max_w // grid_w
        title_h = self.max_h // grid_h

        self.title_size = min(title_w, title_h)

        win_w = self.title_size * grid_w
        win_h = self.title_size * grid_h

        self.screen = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("PacMan")


    def load_spritesheet(self, filepath: str) -> None:
        """Safely load the spritesheet or fallback to basic shapes."""
        try:
            self.sheet = pygame.image.load(filepath).convert()
            transcolor = self.sheet.get_at((0,0))
            self.sheet.set_colorkey(transcolor)

        except (pygame.error, FileNotFoundError) as err:
            print(f"Warning: Could not load spritesheet '{filepath}': {err}")
            self.sheet = None
    
    def get_sprite(self, x: int, y: int, tile_size: int = 16) -> Optional[pygame.Surface]:
        if self.sheet is None:
            return None
        rect = pygame.Rect(x * tile_size, y * tile_size, tile_size * 2, tile_size * 2)
        return cast(pygame.Surface, self.sheet.subsurface(rect))

    def draw_wall(self, x: int, y: int, is_logo: bool = False) -> None:
        if not self.screen:
            return None

        rect = (
            x * self.title_size,
            y * self.title_size,
            self.title_size,
            self.title_size
        )
        color = (0, 100, 255) if is_logo else (0, 0, 255)
        pygame.draw.rect(self.screen, color, rect)

    def load_dot(self, filepath: str) -> None:
        """Load the pacgum dot sprite, or set to None for fallback drawing."""
        try:
            img = pygame.image.load(filepath).convert_alpha()
            self.dot_img = pygame.transform.scale(img, (self.title_size, self.title_size))
        except (pygame.error, FileNotFoundError) as err:
            print(f"Warning: Could not load dot sprite '{filepath}': {err}")
            self.dot_img = None
    
    def load_player_frames(self, base_dir: str) -> None:
        """Load all directional animation frames for pacman."""
        dir_folders = {
            Direction.RIGHT: "pacman-right",
            Direction.LEFT:  "pacman-left",
            Direction.UP:    "pacman-up",
            Direction.DOWN:  "pacman-down",
        }
        for direction, folder in dir_folders.items():
            frames = []
            for i in range(1, 4):
                path = os.path.normpath(os.path.join(base_dir, folder, f"{i}.png"))
                try:
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.scale(img, (self.title_size, self.title_size))
                    frames.append(img)
                except (pygame.error, FileNotFoundError) as err:
                    print(f"Warning: Could not load '{path}': {err}")
            self.player_frames[direction] = frames

    def draw_pacgum(self, x: int, y: int) -> None:
        """Draw a pacgum (small dot) at grid position (x, y)."""
        px = x * self.title_size
        py = y * self.title_size
        if self.dot_img:
            self.screen.blit(self.dot_img, (px, py))
        else:
            cx = px + self.title_size // 2
            cy = py + self.title_size // 2
            r = max(2, self.title_size // 6)
            pygame.draw.circle(self.screen, (255, 220, 50), (cx, cy), r)

    def draw_powergum(self, x: int, y: int) -> None:
        """Draw a power pellet (big pulsing dot) at grid position (x, y)."""
        self._powergum_tick += 1
        pulse = 0.5 + 0.3 * math.sin(self._powergum_tick * 0.15)
        r = max(3, int(self.title_size * pulse * 0.5))
        cx = x * self.title_size + self.title_size // 2
        cy = y * self.title_size + self.title_size // 2
        pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), r)
    
    def draw_player(self, grid_x: int, grid_y: int, direction: Direction, delta_time: float) -> None:
        """Draw pacman at grid position with directional animation."""
        px = grid_x * self.title_size
        py = grid_y * self.title_size

        # Advance animation timer
        self.anim_timer += delta_time
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 3

        # Pick the right direction's frames — remember last non-NONE direction
        if direction != Direction.NONE:
            self.last_dir = direction
        frames = self.player_frames.get(self.last_dir) or self.player_frames.get(Direction.RIGHT)
        if frames:
            self.screen.blit(frames[self.anim_frame], (px, py))

    def render_frame(self) -> None:
        """Flip the display buffer to the monitor."""
        pygame.display.flip()
        


if __name__ == "__main__":
    render = Render()
    loader = MazeLoader()

    # Generate maze first so we know the real grid dimensions
    loader.generate(width=17, height=25, seed=42, pacgum_count=42)
    grid = loader.get_grid()
    grid_width = len(grid[0])
    grid_height = len(grid)

    # Now spawn_point is properly initialized after generate()
    spawn_x, spawn_y = loader.spawn_point
    player = Player(spawn_x, spawn_y)

    # Setup display with actual maze size so the window is fully filled
    render.setup_display(grid_width, grid_height)

    # Load dot sprite (pacgum)
    _dot_path = os.path.join(
        os.path.dirname(__file__),
        "..", "Sprites", "pacman-art", "other", "dot.png"
    )
    render.load_dot(os.path.normpath(_dot_path))
    _player_base = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "Sprites", "pacman-art"
    ))
    render.load_player_frames(_player_base)
    clock = pygame.time.Clock()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    player.set_direction(Direction.UP)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    player.set_direction(Direction.DOWN)
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    player.set_direction(Direction.LEFT)
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    player.set_direction(Direction.RIGHT)

        delta_time = clock.tick(60) / 1000
        player.update(delta_time, grid)

        render.screen.fill((20, 20, 40))

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if (x, y) == loader.spawn_point:
                    pass  # Spawn Point (no tile drawn here)
                elif cell == 0:
                    render.draw_wall(x, y)  # Wall
                elif cell == 4:
                    render.draw_wall(x, y, is_logo=True)  # Logo Wall (The '42')
                elif cell == 2:
                    render.draw_pacgum(x, y)  # Pacgum
                elif cell == 3:
                    render.draw_powergum(x, y)  # Powergum

        render.draw_player(player.grid_x, player.grid_y, player.current_dir, delta_time)

        render.render_frame()

    pygame.quit()