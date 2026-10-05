import pygame
import os
import math
from typing import Optional, cast
from maze_loader import MazeLoader
from player import Player, Direction
from ui_config import UIConfig

class Render:
    def __init__(self, max_width: int = 1260, max_heigth: int = 800) -> None:
        """Initialize the renderer with safe max window bounds."""
        pygame.init()
        self.ui = UIConfig()
        try:
            pacman_icon = os.path.normpath(os.path.join(
            os.path.dirname(__file__), "..", "Assets", "pacman", "pacman-right", "1.png"
            ))
            loaded_img = pygame.image.load(pacman_icon)
            orig_w, orig_h = loaded_img.get_size()
            padded_img = pygame.Surface((orig_w * 2, orig_h * 2), pygame.SRCALPHA)
            padded_img.blit(loaded_img, (orig_w // 2, orig_h // 2))
            pygame.display.set_icon(padded_img)
        except (FileNotFoundError, pygame.error):
            print("Warning: Couldn't load pacman icon")
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
        self.pacman_death: dict = {}
        self.selected_item = 0

        self.grid_w: int = 0
        self.grid_h: int = 0
        self.offset_x: int = 0
        self.offset_y: int = 0

    def setup_display(self, grid_w: int, grid_h: int) -> None:
        """Initialize display with grid dimensions."""
        self.grid_w = grid_w
        self.grid_h = grid_h

        # If a window already exists (e.g. fullscreen set in menu), keep its size
        # and just recalculate tile size and offsets for the new grid.
        if hasattr(self, 'screen') and self.screen is not None:
            cur_w = self.screen.get_width()
            cur_h = self.screen.get_height()
            tile_w = cur_w // grid_w
            tile_h = (cur_h - 50) // grid_h
            self.tile_size = max(1, min(tile_w, tile_h))
            maze_w = self.tile_size * grid_w
            maze_h = self.tile_size * grid_h
            self.offset_x = (cur_w - maze_w) // 2
            self.offset_y = (cur_h - 50 - maze_h) // 2
            return

        # First launch — calculate a tight-fitting window size
        tile_w = self.max_w // grid_w
        tile_h = (self.max_h - 50) // grid_h
        ts = max(1, min(tile_w, tile_h))

        win_w = ts * grid_w
        win_h = (ts * grid_h) + 50

        self.resize(win_w, win_h)
        pygame.display.set_caption("Pac-Man")


    def resize(self, window_w: int, window_h: int) -> None:
        """Recalculate tile size and center offsets upon resize."""
        self.max_w = window_w
        self.max_h = window_h
        self.screen = pygame.display.set_mode((window_w, window_h), pygame.RESIZABLE)

        if self.grid_w > 0 and self.grid_h > 0:
            tile_w = window_w // self.grid_w
            tile_h = (window_h - 50) // self.grid_h
            self.tile_size = max(1, min(tile_w, tile_h))
            maze_w = self.tile_size * self.grid_w
            maze_h = self.tile_size * self.grid_h
            self.offset_x = (window_w - maze_w) // 2
            self.offset_y = (window_h - 50 - maze_h) // 2


    def load_spritesheet(self, filepath: str) -> None:
        """Load the main spritesheet used for ghost/entity sprites."""
        try:
            self.sheet = pygame.image.load(filepath).convert_alpha()
        except (pygame.error, FileNotFoundError) as err:
            print(f"Warning: Could not load spritesheet '{filepath}': {err}")
            self.sheet = None

    def get_sprite(self, col: int, row: int, base: int = 16) -> Optional[pygame.Surface]:
        """Extract a 32x32 sprite using a 16px grid map, then scale it."""
        if self.sheet is None:
            return None
        offset_x = 1
        offset_y = -0.3
        rect = pygame.Rect((col * base) + offset_x, (row * base) + offset_y, base * 2, base * 2)
        try:
            surf = cast(pygame.Surface, self.sheet.subsurface(rect))
        except ValueError:
            return None
        scaled = pygame.transform.scale(surf, (self.tile_size, self.tile_size))
        scaled.set_colorkey((255, 0, 255))
        return scaled

    def load_ghost_assets(self) -> None:
        """Extract 16x16 ghost assets from the main-assetsheet."""
        self.ghost_assets = {
            "Red": self.get_sprite(0, 4),
            "Pink": self.get_sprite(2, 4),
            "Cyan": self.get_sprite(4, 4),
            "Orange": self.get_sprite(6, 4),
            "Flee": self.get_sprite(10, 4),     # Blue ghost is on row 5
            "Flash": self.get_sprite(10, 6),   # White ghost is on row 5
        }

    def load_pacman_death(self) -> None:
        """Load Pac-Man death animation frames from main-assetsheet row 7, cols 0,2,4,..."""
        frames = []
        col = 0
        while True:
            frame = self.get_sprite(col * 2, 12)
            if frame is None:
                break
            frames.append(frame)
            col += 1
        self.pacman_death["frames"] = frames

    def draw_wall(self, x: int, y: int, is_logo: bool = False) -> None:
        """Draw dark fill for wall tile. Borders drawn by draw_walls_grid."""
        if not self.screen:
            return
        fill = (70,191,238) if is_logo else (0,0,0)
        px = x * self.tile_size + self.offset_x
        py = y * self.tile_size + self.offset_y
        pygame.draw.rect(self.screen, fill, pygame.Rect(
            px, py, self.tile_size, self.tile_size
        ))

    def draw_walls_grid(self, grid: list) -> None:
        """Draw wall borders only on edges that face a corridor (not wall-to-wall)."""
        if not self.screen:
            return
        WALL_VALS = {0, 4}
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        ts = self.tile_size
        lw = max(1, ts // 5)

        def is_wall(gx, gy):
            if gx < 0 or gy < 0 or gy >= rows or gx >= cols:
                return True
            return grid[gy][gx] in WALL_VALS

        for gy, row in enumerate(grid):
            for gx, cell in enumerate(row):
                if cell not in WALL_VALS:
                    continue
                color = (50, 100, 255) if cell == 4 else (70,191,238)
                px = gx * ts + self.offset_x
                py = gy * ts + self.offset_y
                if not is_wall(gx, gy - 1):  # top
                    pygame.draw.line(self.screen, color, (px, py), (px + ts, py), lw)
                if not is_wall(gx, gy + 1):  # bottom
                    pygame.draw.line(self.screen, color, (px, py + ts), (px + ts, py + ts), lw)
                if not is_wall(gx - 1, gy):  # left
                    pygame.draw.line(self.screen, color, (px, py), (px, py + ts), lw)
                if not is_wall(gx + 1, gy):  # right
                    pygame.draw.line(self.screen, color, (px + ts, py), (px + ts, py + ts), lw)

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
        px = x * self.tile_size + self.offset_x
        py = y * self.tile_size + self.offset_y
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
        pulse = 0.5 + 0.3 * math.sin(self._powergum_tick * 0.05)
        r = max(3, int(self.tile_size * pulse * 0.5))
        cx = x * self.tile_size + self.offset_x + self.tile_size // 2
        cy = y * self.tile_size + self.offset_y + self.tile_size // 2
        pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), r)

    def draw_player(self, grid_x: int, grid_y: int, direction: Direction, delta_time: float) -> None:
        """Draw pacman at grid position with directional animation."""
        px = grid_x * self.tile_size + self.offset_x
        py = grid_y * self.tile_size + self.offset_y

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
    
    def draw_pacman_death(self, grid_x: int, grid_y: int, frame_idx: int) -> None:
        """Draw one frame of the Pac-Man death animation."""
        frames = self.pacman_death.get("frames", [])
        if not frames:
            return
        frame_idx = max(0, min(frame_idx, len(frames) - 1))
        px = grid_x * self.tile_size + self.offset_x
        py = grid_y * self.tile_size + self.offset_y
        self.screen.blit(frames[frame_idx], (px, py))

    def render_frame(self) -> None:
        """Flip the display buffer to the monitor."""
        pygame.display.flip()

    def draw_ghost(
        self, x: int, y: int, color: str, state_val: int, f_timer: float
    ) -> None:
        """Draw ghost with basic bobbing animation based on state."""
        px = x * self.tile_size + self.offset_x
        py = y * self.tile_size + self.offset_y

        # Simple bobbing animation using the global tick
        offset_y = 2 if self.anim_frame % 2 == 0 else 0

        # State 3 is FLEE, State 4 is EATEN
        if state_val == 3:
            # Flashes between Flee (blue) and Flash (white) only when timer < 2.0s
            if f_timer < 2.0 and self.anim_frame % 2 == 0:
                sprite = self.ghost_assets.get("Flash")
            else:
                sprite = self.ghost_assets.get("Flee")
        else:
            sprite = self.ghost_assets.get(color)

        if sprite:
            self.screen.blit(sprite, (px, py + offset_y))

    def draw_hud(self, score: int, lives: int, time_left: float,
                 level: int, total_levels: int, wave_mode: str,
                 is_eval: bool = False, cheat_str: str = ""
    ) -> None:
        """Draw basic game stats at the bottom of the screen."""
        y_pos = self.screen.get_height() - 40 if is_eval else self.screen.get_height() - 35

        hud_text = (f"Level: {level}/{total_levels}    Score: {score}     "
                    f"Lives: {lives}    Time: {int(time_left)}")
        if is_eval:
            hud_text += f"    Mode: {wave_mode}"

        surf = self.ui.font_hud.render(hud_text, True, (255, 255, 255))
        cx = self.screen.get_width() // 2
        self.screen.blit(surf, surf.get_rect(center=(cx, y_pos + surf.get_height() // 2)))

        if is_eval and cheat_str:
            cheat_surf = self.ui.font_hud.render(cheat_str, True, (255, 255, 0))
            self.screen.blit(cheat_surf, cheat_surf.get_rect(center=(cx, self.screen.get_height() - 15)))

    def draw_name_input(self, name: str, score: int, is_victory: bool) -> None:
        """Draw the post-game screen prompting for player name."""
        self.screen.fill((0, 0, 0))

        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2

        msg = "VICTORY!" if is_victory else "GAME OVER"
        color = (0, 255, 0) if is_victory else (255, 0, 0)

        title = self.ui.font_title.render(msg, True, color)
        score_txt = self.ui.font_regular.render(f"Final Score: {score}", True, (255, 255, 255))
        prompt = self.ui.font_regular.render("Enter Name (Max 10 chars):", True, (255, 255, 255))

        # Name Input Box
        name_txt = self.ui.font_regular.render(name + "_", True, (70,191,238))

        self.screen.blit(title, title.get_rect(center=(cx, cy - 100)))
        self.screen.blit(score_txt, score_txt.get_rect(center=(cx, cy - 40)))
        self.screen.blit(prompt, prompt.get_rect(center=(cx, cy + 30)))
        self.screen.blit(name_txt, name_txt.get_rect(center=(cx, cy + 80)))


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
        "..", "Assets", "pacman", "other", "dot.png"
    )
    render.load_dot(os.path.normpath(_dot_path))
    _player_base = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "Assets", "pacman"
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
