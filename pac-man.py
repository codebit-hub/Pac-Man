"""
Entery point for the game.
Validates CLI arguments, loads the config file and launches the game.
"""

import sys
import os


# Adjusting the game path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.main import Application


def main() -> None:
	"""Validates argv and launches the game"""

	if len(sys.argv) != 2:
		print("Error: Exactly one argument is required.\n"
		      "Usage: python3 pac-man.py config.json")
		sys.exit(1)

	config_file = sys.argv[1]

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
	main()
