"""
Application of the architecture of the C-based MiniLibX API
through a mock MLX wrapper, practicing naming conventions,
workflow, and limitations of MiniLibX.
"""

import pygame
import time


def mlx_init() -> str:
    """Init MLX and launches graphical system."""

    pygame.init()
    return "mlx_connect_ptr"


def mlx_new_window(
    mlx_ptr: str, width: int, height: int, title: str
) -> pygame.Surface:
    """Creates a new fixed-size window."""

    pygame.display.set_caption(title)
    return pygame.display.set_mode((width, height))


if __name__ == "__main__":
    # Init library
    mlx = mlx_init()
    # time.sleep(5)

    # Create window
    window = mlx_new_window(mlx, 400, 300, "MLX Pac-Man Test")
    time.sleep(5)
