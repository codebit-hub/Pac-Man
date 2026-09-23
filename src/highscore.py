"""Manages reading and writing highscores to disk securely."""

import json
import os
from typing import Any


class HighScoreManager:
    """Handles persistent storage of player scores."""

    def __init__(self, filepath: str) -> None:
        """Init manager with file path."""
        self.filepath = filepath
        self.scores: list[dict[str, Any]] = []
        self.load()

    def load(self) -> None:
        """Safely load scores from JSON, ignoring errors."""
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    self.scores = data
        except (json.JSONDecodeError, OSError):
            pass

    def add_score(self, name: str, score: int) -> None:
        """Add new score, sort, and keep top 10."""
        self.scores.append({"name": name, "score": score})
        # Sort descending by score
        self.scores.sort(key=lambda x: x.get("score", 0), reverse=True)
        self.scores = self.scores[:10]
        self.save()

    def save(self) -> None:
        """Write current top 10 to disk."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as file:
                json.dump(self.scores, file, indent=4)
        except OSError as err:
            print(f"Warning: Could not save highscores: {err}")
