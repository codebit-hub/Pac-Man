"""
Manages highscore tracking.
Loads, saves and validates top 10 player scores.
"""

import json
import os
import re
from typing import Any


class HighScoreManager:
    """Reads and writes highscores."""

    def __init__(self, filename: str) -> None:
        """Init the highscore file manager."""
        self.filename = filename
        self.scores: list[dict[str, Any]] = []
        self._load_scores()

    def _load_scores(self) -> None:
        """Safely load scores from JSON, ignoring errors."""
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)

                if isinstance(data, list):
                    valid_scores = []
                    for entry in data:
                        if (isinstance(entry, dict) and 'name' in entry
                            and 'score' in entry
                            and isinstance(entry['score'], int)
                            and entry['score'] >= 0
                        ):
                            valid_scores.append(entry)
                    self.scores = valid_scores
                    self._sort_and_trim()

        except (json.JSONDecodeError, OSError):
            # Failsafe: starting with empty scores if corrupted
            pass

    def _sort_and_trim(self) -> None:
        """Sort by score descending and keep top 10"""

        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:10]

    def add_score(self, name: str, score: int) -> None:
        """Sanitize name and add valid score to leaderboard."""

        # Validating the score
        if not isinstance(score, int) or score < 0:
            return

        # Restrict to alphanumeric + spaces, max 10 chars
        clean_name = re.sub(r'[^a-zA-Z0-9 ]', '', name)[:10].strip()
        if not clean_name:
            clean_name = "ANONYMOUS"

        self.scores.append({'name': clean_name, 'score': score})
        self._sort_and_trim()
        self._save_scores()

    def _save_scores(self) -> None:
        """Write highscores to disk."""

        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(self.scores, file, indent=4)

        except OSError as err:
            print(f"Warning: Could not have saved highscores: {err}")
        #except OSError:
        #   pass
