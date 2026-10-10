"""
Manages game states, transitions and stats.
Tracks game stats and triggers Level transition, Game Over, Victory
"""

from enum import Enum
from typing import Any


class State(Enum):
    """States of the game"""

    # Using Enum to ensure correct naming
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    LEVEL_TRANSITION = 4
    GAME_OVER = 5
    VICTORY = 6


class GameState:
    """Central game state methods, tracking game progress and logic"""

    def __init__(self, config: Any) -> None:
        """Init the game with validated config"""

        self.config = config
        self.state = State.MENU

        # Player stats
        self.score: int = 0
        self.lives: int = self.config.get("lives")
        self.current_level_idx: int = 0

        # Level stats
        self.max_time: float = float(self.config.get("level_max_time"))
        self.time_remaining: float = self.max_time
        self.pacgums_remaining: int = 0

        # Pellet states
        self.is_frightened: bool = False
        self.frigthened_timer: float = 0.0

    def start_game(self) -> None:
        """Reset game stats for a new game"""

        self.score = 0
        self.lives = self.config.get("lives")
        self.current_level_idx = 0
        self.state = State.PLAYING

    def setup_level(self, total_pacgums: int) -> None:
        """Prep up times and counters for a level"""

        self.time_remaining = self.max_time
        self.pacgums_remaining = total_pacgums
        self.is_frightened = False
        self.frigthened_timer = 0.0
        self.state = State.PLAYING

    def update(self, delta_time: float) -> bool:
        """Updates timers and managees state transitions"""

        if self.state != State.PLAYING:
            return False

        # Updates frightened timer
        if self.is_frightened:
            self.frigthened_timer -= delta_time
            if self.frigthened_timer <= 0:
                self.is_frightened = False
                self.frigthened_timer = 0.0

        # Update level countdown timer
        self.time_remaining -= delta_time
        if self.time_remaining <= 0:
            # self.lose_life()
            # Reset time and alert orchestrator of the timeout
            self.time_remaining = self.max_time
            return True

        return False

    def add_score(self, points: int) -> None:
        """Adds points to player's total score"""

        if points > 0:
            self.score += points

    def collect_pacgums(self) -> None:
        """Manages pacgum consumption"""

        pts = self.config.get("points_per_pacgum")
        self.add_score(pts)
        self.pacgums_remaining -= 1

        if self.pacgums_remaining <= 0:
            self._check_victory()

    def collect_super_pacgum(self) -> None:
        """Manages pellet consumption and triggers flee mode"""

        pts = self.config.get("points_per_super_pacgum")
        self.add_score(pts)
        self.is_frightened = True
        # Sets ghosts 7 sec of vulnerability
        self.frigthened_timer = 7.0

    def eat_ghost(self) -> None:
        """Manages eating of frightened ghost"""

        pts = self.config.get("points_per_ghost")
        self.add_score(pts)

    def lose_life(self) -> None:
        """Deducts a life and triggers game over or restart"""

        self.lives -= 1
        if self.lives <= 0:
            self.state = State.GAME_OVER
        else:
            # Time runs out or player dies-> reset clock for retry
            self.time_remaining = self.max_time
            # Main game loop catches this and reset entity positions

            # Reset frightened state to prevent logic and audio bleed-over
            self.is_frightened = False
            self.frigthened_timer = 0.0

    def _check_victory(self) -> None:
        """Manages level progression"""

        self.current_level_idx += 1
        max_levels = self.config.get("levels")

        if self.current_level_idx >= max_levels:
            self.state = State.VICTORY
        else:
            self.state = State.LEVEL_TRANSITION
