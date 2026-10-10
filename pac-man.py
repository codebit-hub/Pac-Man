from src.main import Application
"""
Entery point for the game.
Validates CLI arguments, loads the config file and launches the game.
"""

import sys
import os


# Adjusting the game path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def get_resource_path(relative_path: str) -> str:
    """Provides absolute resource path for PyInstaller."""

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))

    except AttributeError:
        # If not running as a compiled exe, use normal path
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main() -> None:
    """Validates argv and launches the game."""

    if len(sys.argv) > 2:
        print("Error: Maximum one argument is allowed.\n"
              "Usage: 'python3 pac-man.py config.json'")
        sys.exit(1)

    config_arg = sys.argv[1] if len(sys.argv) == 2 else "config.json"
    config_file = get_resource_path(config_arg)

    if not os.path.isfile(config_file):
        print(f"Error: Configuration file '{config_file}' not found.")
        sys.exit(1)

    if not config_file.lower().endswith(".json"):
        print("Error: Configuration file must have .json extension.")
        sys.exit(1)

    try:
        app = Application(config_file)
        app.run()

    except Exception as err:
        print(f"Fatal Error: Could not start the game. Details: {err}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt: Byeee :D")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
