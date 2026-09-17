"""
Configuration module.
Loads and validates JSON config.
Supports comments starting with #.
Ensures save fallbacks for missing or invalid values.
"""

import json
from typing import Any


class ConfigManager:
    """Stores and validates runtime game config"""

    def __init__(self) -> None:
        """Init and set mandatory safe defaults"""

        self._defaults: dict[str, Any] = {
            "game_mode": "game",
            "highscore_filename": "highscore.json",
            "levels": [{"width": 21, "height": 15}],
            "lives": 3,
            "pacgum": 42,
            "points_per_pacgum": 10,
            "points_per_super_pacgum": 50,
            "points_per_ghost": 200,
            "seed": 42,
            "level_max_time": 90
        }
        self._config: dict[str, Any] = self._defaults.copy()

    def load(self, filepath: str) -> None:
        """Loads config from json with comment support"""

        # Container for config raw lines
        raw_lines: list[str] = []

        # Parsing json with comments into raw_lines
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                for line in file:
                    stripped = line.strip()
                    if not stripped.startswith('#'):
                        raw_lines.append(line)

        except (FileNotFoundError, OSError) as err:
            print(f"Warning: Cannot read '{filepath}': {err}")
            print("Notice: Proceeding with default settings.")
            return

        # Validating raw_lines via json.loads()
        # are these lines json format complient
        try:
            content = "".join(raw_lines)
            data = json.loads(content)
            if not isinstance(data, dict):
                print("Warning: JSON is not a dictionary.")
                print("Notice: Proceeding with default settings.")
                return

        except json.JSONDecodeError as err:
            print(f"Warning: JSON syntax error: {err}.")
            print("Check for malformed numbers, syntax or missing quotes.")
            print("Notice: Proceeding with default settings.")
            return

        except Exception as err:
            print(f"Warning: Unexpected error: {err}.")
            print("Notice: Proceeding with default settings.")
            return

        self._apply_data(data)

    def _apply_data(self, data: dict[str, Any]) -> None:
        """Validate parsed JSON data for config"""

        # Report missing keys
        for default_key in self._defaults:
            if default_key not in data:
                print(f"Warning: Missing key '{default_key}'. "
                      f"Using default: {self._defaults[default_key]}")

        for key, value in data.items():
            if key not in self._defaults:
                continue

            expected_type = type(self._defaults[key])

            if not isinstance(value, expected_type):
                print(f"Warning: '{key}' needs {expected_type.__name__}.")
                continue

            # Reset invalid values to safe defaults
            if key == "game_mode" and value not in ("game", "evaluation"):
                print("Warning: invalid game_mode. Reset to 'game'.")
                self._config["game_mode"] = "game"

            elif key == "highscore_filename":
                val_str = str(value).strip()

                # OS forbidden characters for file names
                forbidden = '<>:"/\\|?*'

                # Check for empty, length <256, forbidden chars
                if (
                    not val_str
                    or len(val_str) > 255
                    or any(char in forbidden for char in val_str)
                ):
                    print("Warning: invalid highscore filename. "
                          "Reset to default.")
                    self._config["highscore_filename"] = (
                        self._defaults["highscore_filename"])
                else:
                    self._config["highscore_filename"] = val_str

            elif key == "levels":
                self._config["levels"] = self._validate_levels(value)

            elif key == "lives" and value <= 0:
                print("Warning: 'lives' must be > 0. Reset to 3.")
                self._config["lives"] = 3

            elif key == "pacgum" and value < 0:
                print("Warning: 'pacgum' must be > 0. Reset to default.")
                self._config["pacgum"] = self._defaults["pacgum"]

            elif key.startswith("points_") and value < 0:
                print(f"Warning: '{key}' cannot be < 0. Reset to default.")
                self._config[key] = self._defaults[key]

            elif key == "level_max_time" and value <= 0:
                print("Warning: 'level_max_time' > 0. Reset to 90.")
                self._config["level_max_time"] = 90

            else:
                self._config[key] = value

    def _validate_levels(
            self, levels: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Validate the levels array structure"""

        safe_levels: list[dict[str, Any]] = []
        for lvl in levels:
            if not isinstance(lvl, dict):
                continue

            w = lvl.get("width", 21)
            h = lvl.get("height", 15)

            # Ensuring dimensions are integers and correctly sized
            if not isinstance(w, int) or not (17 <= w <= 35):
                w = 21
            if not isinstance(h, int) or h < 15:
                h = 15
            safe_levels.append({"width": w, "height": h})

        if not safe_levels:
            print("Warning: No valid levels found. Using default.")
            return [{"width": 21, "height": 15}]

        return safe_levels

    def get(self, key: str) -> Any:
        """Retrieve a config value by key"""

        # Enables per config key value retrieval
        return self._config.get(key)


if __name__ == "__main__":
    import os

    print("[*] Running verification tests for ConfigManager...")

    test_file = "config.json"
    if not os.path.exists(test_file):
        test_file = "../"

    cfg = ConfigManager()
    cfg.load(test_file)

    assert cfg.get("game_mode") == "game"
    assert cfg.get("lives") == 3  # Successfully clamped
    assert cfg.get("seed") == 42  # Prevented bad type
    assert cfg.get("unknown_key") is None  # Prevented unknown key

    lvls = cfg.get("levels")
    # assert len(lvls) == 3
    assert lvls[0]["width"] == 21
    assert lvls[0]["height"] == 15

    print("[+] All configuration checks passed.")

    print(f"\n{cfg._config}")
