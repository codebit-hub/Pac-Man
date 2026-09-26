from os import environ
import pygame
import os
import math
from typing import Optional, cast
from maze_loader import MazeLoader
from player import Player, Direction

class Render:
    def __init__(self, max_width: int = 1260, max_heigth: int = 800) -> None:
        """Initialize the renderer with safe max window bounds."""
        pygame.init()
        self.max_w = max_width
        self.max_h = max_heigth
        self.tile_size: int = 16
        self.sheet = None
        self.dot_img: Optional[pygame.Surface] = None
        self._powergum_tick: int = 0
        self.player_frames: dict = {}
        self.anim_frame: int = 0
        self.anim_timer: float = 0.0
        self.ANIM_SPEED: float = 0.1  # seconds per frame
        self.last_dir: Direction = Direction.RIGHT  # fallback facing direction

    def setup_display(self, grid_w: int, grid_h: int) -> None:
        """Calculate tile size and create the Pygame window with HUD space."""
        tile_w = self.max_w // grid_w
        tile_h = (self.max_h - 50) // grid_h  # Reserve 50px for the HUD

        self.tile_size = min(tile_w, tile_h)
        
        win_w = self.tile_size * grid_w
        win_h = (self.tile_size * grid_h) + 50  # Add HUD space to window

        self.screen = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("Pac-Man")

    def load_spritesheet(self, filepath: str) -> None:
        """Safely load the spritesheet or fallback to basic shapes."""
        try:
            self.sheet = pygame.image.load(filepath).convert()
            transcolor = self.sheet.get_at((0,0))
            self.sheet.set_colorkey(transcolor)

        except (pygame.error, FileNotFoundError) as err:
            print(f"Warning: Could not load spritesheet '{filepath}': {err}")
            self.sheet = None

    def get_sprite(self, col: int, row: int, base: int = 16) -> Optional[pygame.Surface]:
        """Extract a 32x32 sprite using a 16px grid map, then scale it."""
        if self.sheet is None:
            return None
        # Vokotera mapped using 16px steps, but the sprites are 32x32
        rect = pygame.Rect(col * base, row * base, base * 2, base * 2)
        surf = cast(pygame.Surface, self.sheet.subsurface(rect))
        return pygame.transform.scale(surf, (self.tile_size, self.tile_size))

    def load_ghost_sprites(self) -> None:
        """Extract 16x16 ghost sprites from the spritesheet."""
        self.ghost_sprites = {
            "Red": self.get_sprite(0, 4),
            "Pink": self.get_sprite(2, 4),
            "Cyan": self.get_sprite(4, 4),
            "Orange": self.get_sprite(6, 4),
            "Flee": self.get_sprite(8, 4),
            "Flash": self.get_sprite(10, 4),
            "Eyes": self.get_sprite(12, 4)
        }

    def draw_wall(self, x: int, y: int, is_logo: bool = False) -> None:
        """Draw continuous solid arcade walls."""
        if not self.screen:
            return

        rect = pygame.Rect(
            x * self.tile_size, y * self.tile_size,
            self.tile_size, self.tile_size
        )
        color = (50, 100, 255) if is_logo else (0, 0, 200)
        pygame.draw.rect(self.screen, color, rect)

    def load_dot(self, filepath: str) -> None:
        """Load the pacgum dot sprite, or set to None for fallback drawing."""
        try:
            img = pygame.image.load(filepath).convert_alpha()
            self.dot_img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
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
                    img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
                    frames.append(img)
                except (pygame.error, FileNotFoundError) as err:
                    print(f"Warning: Could not load '{path}': {err}")
            self.player_frames[direction] = frames

    def draw_pacgum(self, x: int, y: int) -> None:
        """Draw a pacgum (small dot) at grid position (x, y)."""
        px = x * self.tile_size
        py = y * self.tile_size
        if self.dot_img:
            self.screen.blit(self.dot_img, (px, py))
        else:
            cx = px + self.tile_size // 2
            cy = py + self.tile_size // 2
            r = max(2, self.tile_size // 6)
            pygame.draw.circle(self.screen, (255, 220, 50), (cx, cy), r)

    def draw_powergum(self, x: int, y: int) -> None:
        """Draw a power pellet (big pulsing dot) at grid position (x, y)."""
        self._powergum_tick += 1
        pulse = 0.5 + 0.3 * math.sin(self._powergum_tick * 0.15)
        r = max(3, int(self.tile_size * pulse * 0.5))
        cx = x * self.tile_size + self.tile_size // 2
        cy = y * self.tile_size + self.tile_size // 2
        pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), r)

    def draw_player(self, grid_x: int, grid_y: int, direction: Direction, delta_time: float) -> None:
        """Draw pacman at grid position with directional animation."""
        px = grid_x * self.tile_size
        py = grid_y * self.tile_size

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

    def draw_ghost(
        self, x: int, y: int, color: str, state_val: int, f_timer: float
    ) -> None:
        """Draw ghost with basic bobbing animation based on state."""
        px = x * self.tile_size
        py = y * self.tile_size

        # Simple bobbing animation using the global tick
        offset_y = 2 if self.anim_frame % 2 == 0 else 0

        # State 3 is FLEE, State 4 is EATEN
        if state_val == 4:
            sprite = self.ghost_sprites.get("Eyes")
        elif state_val == 3:
            # Flash white if timer is running out (< 2 seconds)
            if f_timer < 2.0 and self.anim_frame % 2 == 0:
                sprite = self.ghost_sprites.get("Flash")
            else:
                sprite = self.ghost_sprites.get("Flee")
        else:
            sprite = self.ghost_sprites.get(color)

        if sprite:
            self.screen.blit(sprite, (px, py + offset_y))

    def draw_hud(self, score: int, lives: int, time_left: float, level: int, wave_mode: str) -> None:
        """Draw basic game stats at the bottom of the screen."""
        if not hasattr(self, 'font'):
            self.font = pygame.font.SysFont(None, 24)

        hud_text = (f"Level: {level}     Score: {score}     Lives: {lives}"
                    f"     Time: {int(time_left)}     Mode: {wave_mode}")
        surf = self.font.render(hud_text, True, (255, 255, 255))
        self.screen.blit(surf, (20, self.screen.get_height() - 35))



if __name__ == "__main__":
    render = Render()
    loader = MazeLoader()

    # Generate maze first so we know the real grid dimensions
    loader.generate(width=15, height=18, seed=42, pacgum_count=42)
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