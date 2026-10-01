*This project has been created as part of the 42 curriculum by dporhomo, vokatera.*

# Pac-Man

## Description

This project is a fully featured, Pygame-based clone of the classic arcade game Pac-Man. It features dynamically generated mazes, classic ghost AI wave behaviors (Scatter, Chase, and Flee), progressive difficulty scaling across multiple levels, and a persistent top-10 highscore system. The application relies on a modular architecture, completely separating backend game logic from front-end rendering.

### Objective

The core objective of this project is to implement robust Object-Oriented Programming (OOP) principles, algorithmic integration, and state-machine architecture. It focuses heavily on safe configuration parsing, robust error handling, frame-independent entity movement, and collaborative software development using an agile Git workflow.

---

## Instructions

### Installation & Setup

Before running the game, you must install the required dependencies, including the Pygame graphics library and the custom `A-Maze-ing` maze generation package.

1. Create and activate a virtual environment (recommended): `python3 -m venv venv && source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt` (Ensure the `A-Maze-ing` package is included or install it locally per the package's documentation).

### Execution

The game requires exactly one configuration file to run safely. Use the entry-point script at the root directory:

```bash
python3 pac-man.py config.json

```

### Output

* **Terminal Output:** The terminal is kept clean during standard gameplay. If an invalid configuration path or missing file is provided, the terminal will output a clean, user-friendly error message detailing the issue and gracefully exit (preventing Python tracebacks).
* **Game Screen:** A dynamic Pygame window will launch, sizing itself based on the level dimensions specified in the config.
* *[Front-end] The game boots into a retro-styled Main Menu featuring animated sprites. During gameplay, you will see the dynamically generated maze, animated entities, and a bottom HUD tracking score, lives, wave modes, and active cheats.*



---

## Configuration

The game logic relies entirely on a mandatory `config.json` file. The backend parses this securely, preventing silent failures (e.g., catching booleans incorrectly parsed as integers).
**Key Structure & Default Behaviors:**

* `game_mode`: Accepts `"game"` or `"evaluation"`. Evaluation mode enables in-game cheats via the Pause menu (invincibility, speed tuning, level skipping).
* `seed`: Integer used to generate Level 1 predictably.
* `levels`: Total number of levels before triggering the Victory state.
* `level`: Array containing objects with `"width"` and `"height"`. The backend calculates dynamic ghost speed scaling from `1.0` to `5.2` across these levels.
* `ghost_behavior_random`: Boolean. If true, dynamically shuffles ghost spawn corners and visual colors upon initialization.
* `highscore_filename`: Standardized path for persistent JSON saving.

---

## Highscore

The project utilizes a persistent Highscore system managed by the `HighScoreManager` class, tracking the Top 10 players.

* **Implementation Choice:** It relies on an external `.json` file. JSON was chosen because it natively serializes Python dictionaries, removing the need for a heavy external database library while keeping the save file human-readable.
* **Robustness:** The backend aggressively validates the data. If the JSON is manually corrupted, missing, or injected with negative scores/invalid types, the system safely catches the `JSONDecodeError` or `OSError` and falls back to an empty list rather than crashing. Player names are sanitized via Regex to enforce alphanumeric characters and a 10-character limit.

---

## Maze Generation

Mazes are generated dynamically using the `A-Maze-ing` package, orchestrated by the `MazeLoader` backend wrapper.

1. Level 1 is explicitly generated using the `seed` provided in the JSON configuration.
2. Subsequent levels drop the config seed and use `random.randint` to ensure unique layouts.
3. The algorithm extracts the raw array from the package, calculates empty corridor space, and safely determines the total number of playable pacgums before seeding the player's spawn point.
4. *[Front-end] The renderer then maps these backend integer values (0, 1, 2, 3, 4) to specific sprites and draws calculated wall-borders dynamically so different sizes fit the window flawlessly.*

---

## Implementation

The backend is built around a central `Application` orchestrator that acts as a finite state machine (`MENU`, `PLAYING`, `PAUSE`, `NAME_INPUT`, `HIGHSCORES`).

**Technical Trade-offs & Features:**

* **Frame-Independent Movement:** Entities use a `delta_time` multiplier synced to the Pygame clock tick. This ensures that Pac-Man and the ghosts move at the exact same logical speed regardless of whether a machine runs at 30 FPS or 144 FPS.
* **Decoupled State:** The backend logic (`GameState`) handles all timers (e.g., Flee mode, Scatter/Chase wave switching) and score aggregation independently of the graphics.
* **Safe Instantiation:** To prevent Pygame from suffering hardware-level crashes during level-reloads (due to ZeroDivisionErrors when evaluation speeds are set to 0.0), the engine calculates and overrides entity attributes securely *after* class initialization.

---

## General Software Architecture

* **`pac-man.py`**: The safe CLI entry point that intercepts tracebacks.
* **`main.py` (`Application`)**: The central hub that routes inputs, handles state transitions, and manages the Pygame event loop.
* **`config.py` / `highscore.py**`: Independent modules dedicated strictly to data serialization and validation.
* **`game_state.py`**: The logical referee tracking lives, points, wave modes, and checking victory conditions.
* **`player.py` / `ghost.py**`: OOP representation of entities containing internal pathfinding checks, direction queues, and speed math.
* **`maze_loader.py`**: An abstraction layer specifically for interacting with the external `A-Maze-ing` package.
* *[Front-end] `menu.py` / `renderer.py`: Handles all Pygame surface drawing, alpha-transparency overlays, dynamic scaling math, and spritesheet extraction.*

---

## Project Management

We utilized an Agile Git workflow strictly managed through GitHub to ensure continuous integration and stable builds.

* **Branching Strategy:** Work was divided into `Front_end_dev` and `Back_end_dev` branches. Team members pushed small, functional commits frequently.
* **Pull Requests:** Stable features were merged back into the `main` branch solely through Pull Requests to prevent regressions.
* **Task Tracking:** GitHub Issues were used as tickets to assign specific feature modules or bug fixes (e.g., fixing Pygame window shrinking).
* **Communication:** GitHub Discussions were leveraged alongside daily coding check-ins.
* **Documentation:** Detailed management artifacts can be found in the [Project Management Directory](https://www.google.com/search?q=./docs/project_management/).

---

## Resources

* [The Pac-Man Dossier](https://www.google.com/search?q=https://pacman.holenet.info/) - Used to understand classic ghost AI targeting (Scatter, Chase, Flee).
* [Pygame Documentation](https://www.google.com/search?q=https://www.pygame.org/docs/) - Referenced for event handling and `Surface` alpha blending.
* **AI Usage (Gemini/ChatGPT):** AI tools were utilized specifically as thought partners and code reviewers. They were used to help track down obscure hardware-specific Pygame crashes (e.g., full-screen toggling context crashes), debug coordinate math for the pause menu overlap, and format regex patterns for the Highscore validation backend.