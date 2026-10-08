import pygame
import os
import math
from typing import Optional, cast

from maze_loader import MazeLoader
from player import Player, Direction
from ui_config import UIConfig


class MLXUtils:
    """Utility class for MLX-compliant operations."""

    @staticmethod
    def scale_image(
            surf: pygame.Surface, new_w: int, new_h: int
    ) -> pygame.Surface:
        """
        Nearest-neighbor image scale using pixel-level.
        """
        src_w = surf.get_width()
        src_h = surf.get_height()
        if src_w == 0 or src_h == 0 or new_w <= 0 or new_h <= 0:
            return pygame.Surface((max(1, new_w), max(1, new_h)))
        if src_w == new_w and src_h == new_h:
            return surf.copy()
        has_alpha = bool(surf.get_flags() & pygame.SRCALPHA)
        result = pygame.Surface(
            (new_w, new_h), pygame.SRCALPHA if has_alpha else 0
        )
        for dst_y in range(new_h):
            src_y = min(int(dst_y * src_h / new_h), src_h - 1)
            for dst_x in range(new_w):
                src_x = min(int(dst_x * src_w / new_w), src_w - 1)
                result.set_at((dst_x, dst_y), surf.get_at((src_x, src_y)))
        colorkey = surf.get_colorkey()
        if colorkey is not None:
            result.set_colorkey(colorkey)
        return result

    @staticmethod
    def colorize_icon(surf: pygame.Surface, add_r: int, add_g: int, add_b: int) -> pygame.Surface:
        """
        Pixel-by-pixel color tinting.
        MLX-compliant replacement for pygame.BLEND_RGB_ADD.
        Equivalent to looping mlx_get_data_addr and manipulating RGB values.
        """
        result = surf.copy()
        for x in range(result.get_width()):
            for y in range(result.get_height()):
                r, g, b, a = result.get_at((x, y))
                if a > 0:
                    result.set_at((x, y), (
                        min(255, r + add_r),
                        min(255, g + add_g),
                        min(255, b + add_b),
                        a
                    ))
        return result

    @staticmethod
    def draw_rect(surf: pygame.Surface, color: tuple, rect: pygame.Rect, width: int = 0):
        """MLX-compliant rectangle drawing (pixel by pixel)."""
        x_start, y_start, w, h = int(rect.x), int(rect.y), int(rect.w), int(rect.h)
        if width == 0:
            for y in range(max(0, y_start), min(surf.get_height(), y_start + h)):
                for x in range(max(0, x_start), min(surf.get_width(), x_start + w)):
                    surf.set_at((x, y), color)
        else:
            MLXUtils.draw_line(surf, color, (x_start, y_start), (x_start + w - 1, y_start), width)
            MLXUtils.draw_line(surf, color, (x_start, y_start + h - 1), (x_start + w - 1, y_start + h - 1), width)
            MLXUtils.draw_line(surf, color, (x_start, y_start), (x_start, y_start + h - 1), width)
            MLXUtils.draw_line(surf, color, (x_start + w - 1, y_start), (x_start + w - 1, y_start + h - 1), width)

    @staticmethod
    def draw_line(surf: pygame.Surface, color: tuple, start: tuple, end: tuple, width: int = 1):
        """MLX-compliant line drawing (Bresenham's algorithm)."""
        x0, y0 = int(start[0]), int(start[1])
        x1, y1 = int(end[0]), int(end[1])
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for wx in range(width):
                for wy in range(width):
                    px, py = x0 + wx, y0 + wy
                    if 0 <= px < surf.get_width() and 0 <= py < surf.get_height():
                        surf.set_at((px, py), color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    @staticmethod
    def draw_circle(surf: pygame.Surface, color: tuple, center: tuple, radius: int, width: int = 0):
        """MLX-compliant circle drawing."""
        cx, cy = int(center[0]), int(center[1])
        r2 = radius * radius
        if width == 0:
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    if x * x + y * y <= r2:
                        px, py = cx + x, cy + y
                        if 0 <= px < surf.get_width() and 0 <= py < surf.get_height():
                            surf.set_at((px, py), color)
        else:
            in_r2 = (radius - width) * (radius - width)
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    d2 = x * x + y * y
                    if in_r2 <= d2 <= r2:
                        px, py = cx + x, cy + y
                        if 0 <= px < surf.get_width() and 0 <= py < surf.get_height():
                            surf.set_at((px, py), color)

    @staticmethod
    def draw_triangle(surf: pygame.Surface, color: tuple, p1: tuple, p2: tuple, p3: tuple):
        """MLX-compliant filled triangle drawing."""
        min_x = int(min(p1[0], p2[0], p3[0]))
        max_x = int(max(p1[0], p2[0], p3[0]))
        min_y = int(min(p1[1], p2[1], p3[1]))
        max_y = int(max(p1[1], p2[1], p3[1]))

        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(surf.get_width() - 1, max_x)
        max_y = min(surf.get_height() - 1, max_y)

        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                d1 = sign((x, y), p1, p2)
                d2 = sign((x, y), p2, p3)
                d3 = sign((x, y), p3, p1)
                has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
                has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
                if not (has_neg and has_pos):
                    surf.set_at((x, y), color)


class Render:
    def __init__(self, max_width: int = 1260, max_heigth: int = 800) -> None:
        """Initialize the renderer with safe max window bounds."""
        # 1. Initialization and UI
        pygame.init()
        self.ui = UIConfig()
        self.ui.load_icon()

        # 2. Sizes of window
        self.max_w = max_width
        self.max_h = max_heigth
        self.default_max_w = max_width
        self.default_max_h = max_heigth

        # 3. Grid
        self.tile_size: int = 16
        self.grid_w: int = 0
        self.grid_h: int = 0
        self.offset_x: int = 0
        self.offset_y: int = 0

        # 4. Textures and graphics
        self.sheet: Optional[pygame.Surface] = None
        self.dot_img: Optional[pygame.Surface] = None
        self.player_frames: dict = {}
        self.pacman_death: dict = {}

        # 5. Animations
        self.ANIM_SPEED: float = 0.1
        self.anim_timer: float = 0.0
        self.anim_frame: int = 0
        self._powergum_tick: int = 0

        # 6. Game and UI States
        self.last_dir: Direction = Direction.RIGHT  # fallback facing direction
        self.selected_item = 0

    def setup_display(self, grid_w: int, grid_h: int) -> None:
        """Initialize display with grid dimensions."""
        self.grid_w = grid_w
        self.grid_h = grid_h

        if (hasattr(self, 'screen')
                and self.screen is not None):
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

        # First launch
        tile_w = self.max_w // grid_w
        tile_h = (self.max_h - 50) // grid_h
        ts = max(1, min(tile_w, tile_h))

        win_w = ts * grid_w
        win_h = (ts * grid_h) + 50

        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.resize(win_w, win_h)
        pygame.display.set_caption("Pac-Man")

    def restore_window(self) -> None:
        """Restore the window after fullscreen"""
        if self.grid_w > 0 and self.grid_h > 0:
            tile_w = self.default_max_w // self.grid_w
            tile_h = (self.default_max_h - 50) // self.grid_h
            ts = max(1, min(tile_w, tile_h))
            win_w = ts * self.grid_w
            win_h = (ts * self.grid_h) + 50
            os.environ['SDL_VIDEO_CENTERED'] = '1'
            self.screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
            self.resize(win_w, win_h)

    def resize(self, window_w: int, window_h: int) -> None:
        """Recalculate tile size and center offsets upon resize."""
        self.max_w, self.max_h = window_w, window_h
        size = (window_w, window_h)
        self.screen = pygame.display.set_mode(size, pygame.RESIZABLE)

        if self.grid_w > 0 and self.grid_h > 0:
            tile_w = window_w // self.grid_w
            tile_h = (window_h - 50) // self.grid_h
            self.tile_size = max(1, min(tile_w, tile_h))
            maze_w = self.tile_size * self.grid_w
            maze_h = self.tile_size * self.grid_h
            self.offset_x = (window_w - maze_w) // 2
            self.offset_y = (window_h - 50 - maze_h) // 2

        self.reload_scales()

    def reload_scales(self) -> None:
        """Rescale all textures based on current tile_size."""
        if hasattr(self, 'orig_dot_img') and self.orig_dot_img:
            self.dot_img = MLXUtils.scale_image(self.orig_dot_img, self.tile_size, self.tile_size)

        if hasattr(self, 'orig_player_frames') and self.orig_player_frames:
            p_size = max(1, int(self.tile_size * 0.8))
            for dir_key, orig_frames in self.orig_player_frames.items():
                rescaled = []
                for f in orig_frames:
                    s = MLXUtils.scale_image(f, p_size, p_size)
                    s.set_colorkey((255, 0, 255))
                    rescaled.append(s)
                self.player_frames[dir_key] = rescaled

        if self.sheet:
            self.load_ghost_assets()
            self.load_pacman_death()

    def load_spritesheet(self, filepath: str) -> None:
        """Load the main spritesheet used for ghost/entity sprites."""
        try:
            self.sheet = pygame.image.load(filepath).convert_alpha()
        except (pygame.error, FileNotFoundError) as err:
            print(f"Warning: Could not load spritesheet '{filepath}': {err}")
            self.sheet = None

    def get_sprite(self, col: int, row: int) -> Optional[pygame.Surface]:
        """Extract each entity in correct form"""
        if self.sheet is None:
            return None

        base = 16
        x = (col * base) + 1
        y = (row * base) + 0
        rect = pygame.Rect(x, y, base * 2, base * 2)

        try:
            surf = cast(pygame.Surface, self.sheet.subsurface(rect))
        except ValueError:
            return None

        p_size = max(1, int(self.tile_size * 0.8))
        scaled = MLXUtils.scale_image(surf, p_size, p_size)
        scaled.set_colorkey((255, 0, 255))
        return scaled

    def load_ghost_assets(self) -> None:
        """Extract ghost assets from the main-spiresheet."""
        self.ghost_assets = {
            "Red": self.get_sprite(0, 4),
            "Pink": self.get_sprite(2, 4),
            "Cyan": self.get_sprite(4, 4),
            "Orange": self.get_sprite(6, 4),
            "Flee": self.get_sprite(10, 4),
            "Flash": self.get_sprite(10, 6),
        }

    def load_pacman_death(self) -> None:
        """Load Pac-Man death animation frames from main-spiresheet."""
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
        fill = self.ui.GAME_PURPLE if is_logo else self.ui.C_BG
        px = x * self.tile_size + self.offset_x
        py = y * self.tile_size + self.offset_y
        MLXUtils.draw_rect(self.screen, fill,
                           pygame.Rect(px, py, self.tile_size, self.tile_size))

    def draw_walls_grid(self, grid: list) -> None:
        """Draw wall borders only on edges that face a corridor"""
        if not self.screen:
            return
        WALL_VALS = {0, 4}
        rows = len(grid)
        cols = len(grid[0])
        ts = self.tile_size
        lw = max(1, ts // 5)

        surf = self.screen
        draw_line = MLXUtils.draw_line

        def is_wall(gx: int, gy: int) -> bool:
            "Returns if its in game map or its wall"
            if gx < 0 or gy < 0 or gy >= rows or gx >= cols:
                return True
            return grid[gy][gx] in WALL_VALS

        for gy, row in enumerate(grid):
            for gx, cell in enumerate(row):
                if cell not in WALL_VALS:
                    continue
                color = self.ui.GAME_PURPLE
                px = gx * ts + self.offset_x
                py = gy * ts + self.offset_y
                px2 = px + ts
                py2 = py + ts
                if not is_wall(gx, gy - 1):  # top
                    draw_line(surf, color, (px, py), (px2, py), lw)
                if not is_wall(gx, gy + 1):  # bottom
                    draw_line(surf, color, (px, py + ts), (px2, py2), lw)
                if not is_wall(gx - 1, gy):  # left
                    draw_line(surf, color, (px, py), (px, py2), lw)
                if not is_wall(gx + 1, gy):  # right
                    draw_line(surf, color, (px + ts, py), (px2, py2), lw)

    def load_dot(self, filepath: str) -> None:
        """Load the pacgum dot sprite"""
        try:
            self.orig_dot_img = pygame.image.load(filepath).convert_alpha()
            self.dot_img = MLXUtils.scale_image(
                self.orig_dot_img, self.tile_size, self.tile_size)
        except (pygame.error, FileNotFoundError) as err:
            print(f"Warning: Could not load dot sprite '{filepath}': {err}")
            self.dot_img = None

    def load_player_frames(self, base_dir: str = "") -> None:
        """Load all directional Pac-Man animation frames from the spritesheet."""
        if not hasattr(self, 'orig_player_frames'):
            self.orig_player_frames = {}

        if self.sheet is None:
            return

        base = 16
        p_size = max(1, int(self.tile_size * 0.8))

        dir_cols = {
            Direction.RIGHT: 2,
            Direction.LEFT: 0,
            Direction.DOWN: 4,
            Direction.UP: 6,
        }

        for direction, col in dir_cols.items():
            orig_frames: list = []
            scaled_frames: list = []
            for anim_row in (0, 2):
                x = col * base + 1
                y = anim_row * base
                rect = pygame.Rect(x, y, base * 2, base * 2)

                if x + rect.w <= self.sheet.get_width() and y + rect.h <= self.sheet.get_height():
                    try:
                        raw = self.sheet.subsurface(rect).copy()
                        raw.set_colorkey((255, 0, 255))
                        orig_frames.append(raw)

                        scaled = MLXUtils.scale_image(raw, p_size, p_size)
                        scaled.set_colorkey((255, 0, 255))
                        scaled_frames.append(scaled)
                    except ValueError:
                        pass

            # If no frames loaded, use a solid color fallback to avoid crashes
            if not orig_frames:
                surf = pygame.Surface((base * 2, base * 2))
                surf.fill((255, 255, 0))  # Yellow square fallback
                orig_frames.append(surf)
                scaled_frames.append(MLXUtils.scale_image(surf, p_size, p_size))

            # Attempt to load completely closed mouth (typically col 8, row 0)
            closed_col = 8
            closed_row = 0
            cx = closed_col * base + 1
            cy = closed_row * base
            crect = pygame.Rect(cx, cy, base * 2, base * 2)

            if cx + crect.w <= self.sheet.get_width() and cy + crect.h <= self.sheet.get_height():
                try:
                    craw = self.sheet.subsurface(crect).copy()
                    craw.set_colorkey((255, 0, 255))
                    orig_frames.append(craw)

                    cscaled = MLXUtils.scale_image(craw, p_size, p_size)
                    cscaled.set_colorkey((255, 0, 255))
                    scaled_frames.append(cscaled)
                except ValueError:
                    pass

            # Fallback for the 3rd frame if loading the closed mouth failed
            while len(orig_frames) < 3:
                orig_frames.append(orig_frames[1] if len(orig_frames) > 1 else orig_frames[0])
                scaled_frames.append(scaled_frames[1] if len(scaled_frames) > 1 else scaled_frames[0])

            self.orig_player_frames[direction] = orig_frames
            self.player_frames[direction] = scaled_frames

    def draw_pacgum(self, x: int, y: int) -> None:
        """Draw a pacgum (small dot) at grid position."""
        px = x * self.tile_size + self.offset_x
        py = y * self.tile_size + self.offset_y
        if self.dot_img:
            self.screen.blit(self.dot_img, (px, py))
        else:
            cx = px + self.tile_size // 2
            cy = py + self.tile_size // 2
            r = max(2, self.tile_size // 6)
            MLXUtils.draw_circle(self.screen, self.ui.C_TEXT_WHITE, (cx, cy), r)

    def draw_powergum(self, x: int, y: int) -> None:
        """Draw a power pellet (big pulsing dot) at grid position (x, y)."""
        self._powergum_tick += 1
        pulse = 0.5 + 0.3 * math.sin(self._powergum_tick * 0.05)
        r = max(3, int(self.tile_size * pulse * 0.5))
        cx = x * self.tile_size + self.offset_x + self.tile_size // 2
        cy = y * self.tile_size + self.offset_y + self.tile_size // 2
        MLXUtils.draw_circle(self.screen, self.ui.C_TEXT_WHITE, (cx, cy), r)

    def draw_player(self, grid_x: int, grid_y: int,
                    direction: Direction, delta_time: float) -> None:
        """Draw pacman at grid position with directional animation."""
        px = grid_x * self.tile_size + self.offset_x + 2.5
        py = grid_y * self.tile_size + self.offset_y + 2.5

        self.anim_timer += delta_time
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % 3

        if direction != Direction.NONE:
            self.last_dir = direction
        fallback = self.player_frames.get(Direction.RIGHT)
        frames = self.player_frames.get(self.last_dir, fallback)

        if frames:
            img = frames[self.anim_frame]
            offset_center = (self.tile_size - img.get_width()) // 2
            self.screen.blit(img, (px + offset_center, py + offset_center))

    def draw_pacman_death(self, grid_x: int, grid_y: int,
                          frame_idx: int) -> None:
        """Draw one frame of the Pac-Man death animation."""
        frames = self.pacman_death.get("frames", [])
        if not frames:
            return
        frame_idx = max(0, min(frame_idx, len(frames) - 1))
        px = grid_x * self.tile_size + self.offset_x
        py = grid_y * self.tile_size + self.offset_y

        img = frames[frame_idx]
        offset_center = (self.tile_size - img.get_width()) // 2
        self.screen.blit(img, (px + offset_center, py + offset_center))

    def render_frame(self) -> None:
        """Flip the display buffer to the monitor."""
        pygame.display.flip()

    def draw_ghost(
        self, x: int, y: int, color: str, state_val: int, f_timer: float
    ) -> None:
        """Draw ghost with basic bobbing animation based on state."""
        px = x * self.tile_size + self.offset_x
        py = y * self.tile_size + self.offset_y

        offset_y = 2 if self.anim_frame % 2 == 0 else 0

        if state_val == 3:
            if f_timer < 2.0 and self.anim_frame % 2 == 0:
                sprite = self.ghost_assets.get("Flash")
            else:
                sprite = self.ghost_assets.get("Flee")
        else:
            sprite = self.ghost_assets.get(color)

        if sprite:
            offset_center = (self.tile_size - sprite.get_width()) // 2
            self.screen.blit(sprite, (px + offset_center + 2, py + offset_y + offset_center + 2))

    def draw_hud(self, score: int, lives: int, time_left: float,
                 level: int, total_levels: int, wave_mode: str,
                 is_eval: bool = False, cheat_str: str = "") -> None:
        """Draw basic game stats at the bottom of the screen."""
        sh = self.screen.get_height()
        cx = self.screen.get_width() // 2
        y_pos = sh - 40 if is_eval else sh - 35

        hud_text = (f"Level: {level}/{total_levels}    Score: {score}     "
                    f"Lives: {lives}    Time: {int(time_left)}")
        if is_eval:
            hud_text += f"    Mode: {wave_mode}"

        surf = self.ui.font_hud.render(hud_text, True, self.ui.C_TEXT_WHITE)
        rect = surf.get_rect(center=(cx, y_pos + surf.get_height() // 2))
        self.screen.blit(surf, rect)

        if is_eval and cheat_str:
            color = self.ui.C_TEXT_YELLOW
            c_surf = self.ui.font_hud.render(cheat_str, True, color)
            c_rect = c_surf.get_rect(center=(cx, sh - 15))
            self.screen.blit(c_surf, c_rect)

    def draw_name_input(self, name: str, score: int, is_victory: bool) -> None:
        """Draw the post-game screen prompting for player name."""
        self.screen.fill(self.ui.C_BG)

        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2

        msg = "VICTORY!" if is_victory else "GAME OVER"
        color = (0, 255, 0) if is_victory else (255, 0, 0)

        title = self.ui.font_title.render(msg, True, color)
        score_msg = f"Final Score: {score}"
        color = self.ui.C_TEXT_WHITE
        score_txt = self.ui.font_regular.render(score_msg, True, color)
        prompt_msg = "Enter Name (Max 10 chars):"
        prompt = self.ui.font_regular.render(prompt_msg, True, color)

        # Name Input Box
        color = self.ui.C_TEXT_PURPLE
        name_txt = self.ui.font_regular.render(name + "_", True, color)

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
        "..", "assets", "pacman", "other", "dot.png"
    )
    render.load_dot(os.path.normpath(_dot_path))
    _sheet_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "assets", "spritesheets", "main-spritesheet.png"
    ))
    render.load_spritesheet(_sheet_path)
    render.load_player_frames()
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
                    render.draw_wall(x, y, is_logo=True)
                elif cell == 2:
                    render.draw_pacgum(x, y)  # Pacgum
                elif cell == 3:
                    render.draw_powergum(x, y)  # Powergum

        render.draw_player(player.grid_x, player.grid_y,
                           player.current_dir, delta_time)

        render.render_frame()

    pygame.quit()
