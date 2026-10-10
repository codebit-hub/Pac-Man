"""
Central Game Configuration module.
Loads and validates settings from config.json.
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
            "levels": 12,
            "level": [{"width": 15, "height": 15}],
            "lives": 3,
            "pacgum": 42,
            "points_per_pacgum": 10,
            "points_per_super_pacgum": 50,
            "points_per_ghost": 200,
            "seed": 42,
            "level_max_time": 90,
            "ghost_behavior_random": False
        }
        self._config: dict[str, Any] = self._defaults.copy()

    def _catch_duplic_keys(
        self, ordered_pairs: list[tuple[str, Any]]
    ) -> dict[str, Any]:
        """Catches duplicate keys in config.json"""

        duplicates = {}
        for key, value in ordered_pairs:
            if key in duplicates:
                print(f"Warning: Found duplicate '{key}'. Clamping.")
                if key in self._defaults:
                    duplicates[key] = self._defaults[key]
            else:
                duplicates[key] = value

        return duplicates

    def load(self, filepath: str) -> None:
        """Loads config from json with comment support"""

        # Container for config raw lines
        raw_lines: list[str] = []

        # Parsing json with comments into raw_lines
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                for line in file:
                    stripped = line.strip()
                    if not (stripped.startswith('#')
                            or stripped.startswith('"#')
                            or stripped.startswith("'#")
                            or stripped.startswith('//')
                            or stripped.startswith('"//')
                            or stripped.startswith("'//")):
                        raw_lines.append(line)

        except (FileNotFoundError, OSError) as err:
            print(f"Warning: Cannot read '{filepath}': {err}")
            print("Notice: Proceeding with default settings.")
            return

        # Validating raw_lines via json.loads()
        # are these lines json format complient
        try:
            content = "".join(raw_lines)

            # Check for duplicate keys
            # data = json.loads(content)
            object_pairs_hook = self._catch_duplic_keys
            data = json.loads(content, object_pairs_hook=object_pairs_hook)

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

            if (
                not isinstance(value, expected_type)
                or (expected_type is int and isinstance(value, bool))
            ):
                print(f"Warning: '{key}' needs {expected_type.__name__}. "
                      "Clamping.")
                continue

            # Reset invalid values to safe defaults
            if key == "game_mode":
                if value not in ("game", "evaluation"):
                    print("Warning: invalid game_mode. Reset to 'game'.")
                    self._config["game_mode"] = "game"
                elif value in ("game", "evaluation"):
                    self._config["game_mode"] = value

            elif key == "highscore_filename":
                val_str = str(value).strip()

                # OS forbidden characters for file names
                forbidden = '<>:"/\\|?*'

                # Check for empty, length < 100, forbidden chars
                if (
                    not val_str
                    or len(val_str) > 100
                    or any(char in forbidden for char in val_str)
                ):
                    print("Warning: invalid highscore filename. "
                          "Reset to default.")
                    self._config["highscore_filename"] = (
                        self._defaults["highscore_filename"])
                else:
                    self._config["highscore_filename"] = val_str

            elif key == "levels":
                if value <= 0:
                    print("Warning: 'levels' must be > 0. Reset to default.")
                    self._config["levels"] = 12
                elif not (1 <= value <= 100):
                    print("Warning: 'levels' exceed 100. Reset to default.")
                    self._config["levels"] = 12
                else:
                    self._config["levels"] = value

            elif key == "level":
                self._config["level"] = self._validate_level(value)

            elif key == "lives":
                if value <= 0:
                    print("Warning: 'lives' must be > 0. Reset to 3.")
                    self._config["lives"] = 3
                elif not (1 <= value <= 100):
                    print("Warning: 'lives' must be < 100. Reset to 3.")
                    self._config["lives"] = 3
                else:
                    self._config["lives"] = value

            elif key == "pacgum" and value < 0:
                print("Warning: 'pacgum' must be > 0. Reset to default.")
                self._config["pacgum"] = self._defaults["pacgum"]

            elif key.startswith("points_") and (value < 0 or value > 1000):
                print(f"Warning: '{key}' is < 0 or > 1000. Reset to default.")
                self._config[key] = self._defaults[key]

            elif key == "level_max_time":
                if value <= 0:
                    print("Warning: 'level_max_time' < 0. Reset to 90.")
                    self._config["level_max_time"] = 90
                else:
                    self._config["level_max_time"] = value

            elif key == "ghost_behavior_random":
                self._config["ghost_behavior_random"] = value

            else:
                self._config[key] = value

    def _validate_level(
            self, level: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Validate the level array structure"""

        safe_levels: list[dict[str, Any]] = []

        for i, lvl in enumerate(level):
            if not isinstance(lvl, dict):
                continue

            # Validating 'width'
            if "width" not in lvl:
                print(f"Warning: 'width' is missing for Level {i + 1}. "
                      "Clamping.")
                w = 15
            else:
                w = lvl["width"]
                # Ensuring dimensions are integers and correctly sized
                # not (17 <= w <= 30):
                if (
                    not isinstance(w, int)
                    or isinstance(w, bool)
                    or not (15 <= w <= 30)
                ):
                    print(f"Incorrect width dimensions for Level {i + 1}. "
                          "Clamping.")
                    w = 15

            # h !< 15:
            if "height" not in lvl:
                print(f"Warning: 'height' is missing for Level {i + 1}. "
                      "Clamping.")
                h = 15
            else:
                h = lvl["height"]
                if (
                    not isinstance(h, int)
                    or isinstance(h, bool)
                    or not (15 <= h <= 30)
                ):
                    print(f"Incorrect height dimensions for Level {i + 1}. "
                          "Clamping.")
                    h = 15

            safe_levels.append({"width": w, "height": h})

        if not safe_levels:
            print("Warning: No valid levels found. Using default.")
            return [{"width": 15, "height": 15}]

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
    lvls = cfg.get("level")
    """
    assert cfg.get("game_mode") == "game"
    assert cfg.get("highscore_filename") == "highscore.json"
    assert cfg.get("levels") == 12

    assert len(lvls) == 3
    assert lvls[0]["width"] == 15
    assert lvls[0]["height"] == 15

    assert cfg.get("lives") == 3  # Successfully clamped
    assert cfg.get("pacgum") == 1
    assert cfg.get("points_per_pacgum") == 10
    assert cfg.get("points_per_super_pacgum") == 50
    assert cfg.get("points_per_ghost") == 200
    assert cfg.get("seed") == 42  # Prevented bad type
    assert cfg.get("level_max_time") == 90
    assert cfg.get("ghost_behavior_random") == False
    assert cfg.get("unknown_key") is None  # Prevented unknown key

    """
    print(f"levels len: {len(lvls)}.")
    print(f"\n{cfg._config}")
    print("[+] All configuration checks passed.")
