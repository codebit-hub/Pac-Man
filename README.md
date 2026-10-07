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

## Packaging & Deployment

This project includes an automated build pipeline via `PyInstaller` to generate a standalone Linux executable. This executable bundles the Python interpreter, all dependencies, and all required static assets (audio, fonts, images) into a single directory, meaning the game can be played on compatible Linux machines without installing Python or cloning this repository.

### How to Build the Package Natively

If you wish to compile the standalone package yourself from the source code:

1. Ensure your virtual environment is active.
2. Run the build command from the root of the repository:
```bash
make build

```


3. The resulting standalone game directory will be placed in `dist/pac-man/`. You can zip this folder to distribute it.

### How to Download and Play the Pre-Compiled Build (Evaluators)

A pre-compiled Linux build has been uploaded as an unlisted, restricted project on Itch.io.

1. **Access the Build:** Navigate to the secret URL provided for the evaluation: `https://codebit.itch.io/pac-man?secret=sOjS0gzLesg7acxiciNWgciemk`
2. **Download:** Click the "Download" button to save the `pac-man-linux.zip` file to your computer.
3. **Extract:** Unzip the downloaded file:
```bash
unzip pac-man-linux.zip -d pac-man-game

```


4. **Launch:** Navigate into the extracted directory and run the standalone executable:
```bash
cd pac-man-game
./pac-man

```


*(Note: The executable automatically discovers the bundled `config.json` and assets; no command-line arguments are required).*

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

* **Frame-Independent Movement:**

Entities use a `delta_time` multiplier synced to the Pygame clock tick. This ensures that Pac-Man and the ghosts move at the exact same logical speed regardless of whether a machine runs at 30 FPS or 144 FPS.

* **Decoupled State:**

The backend logic (`GameState`) handles all timers (e.g., Flee mode, Scatter/Chase wave switching) and score aggregation independently of the graphics.

* **Safe Instantiation:**

To prevent Pygame from suffering hardware-level crashes during level-reloads (due to ZeroDivisionErrors when evaluation speeds are set to 0.0), the engine calculates and overrides entity attributes securely *after* class initialization.

* **Technical Trade-offs & MLX Compliance:**

To strictly adhere to the MLX graphics library constraints, high-level Pygame drawing methods were entirely stripped out and replaced with a custom MLXUtils wrapper that simulates low-level mlx_pixel_put operations using pixel-by-pixel rendering algorithms like Bresenham's. While this successfully fulfilled the architectural requirement, running pure Python loops over thousands of pixels per frame introduced a severe CPU bottleneck that artificially inflated the frame time (delta_time). Because the engine relies on frame-independent movement logic, these massive rendering delays originally caused entities to "teleport" across multiple tiles in a single frame, resulting in Pac-Man phasing through pacgums without triggering consumption checks. Rather than over-engineering a complex ray-casting collision system to catch intermediate tile overlaps, we implemented an elegant mathematical compromise: capping the maximum delta_time sent to the engine at exactly 0.2 seconds. Since Pac-Man requires exactly 0.2 seconds to cross a single tile at his default speed, this cap mathematically restricts him to moving a maximum of one tile per frame. This trade-off flawlessly eliminates collision skipping and naturally syncs the backend game clock with the physical rendering lag, keeping the game perfectly playable despite the heavy pixel-drawing overhead.

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


---

## Resources

## Resources
### General and Algorithmic Research
* [The Pac-Man Dossier](https://pacman.holenet.info/) - A foundational reference for understanding the original Pac-Man ruleset, ghost targeting behavior, maze logic, and the classic Scatter, Chase, and Frightened modes. It was especially useful for validating the game’s AI decisions against the canonical arcade model.
* [Pac-Man Ghost AI Explained](https://www.youtube.com/watch?v=ataGotQ7ir8) - A practical video breakdown of the ghost AI system, helping clarify how each ghost uses different target vectors and behavior phases to create the classic arcade pacing and difficulty curve.
* [Learn the Ghost Movement Patterns](https://www.youtube.com/watch?v=8RLq4QLwoGA) - A visual guide to ghost movement logic and pattern transitions, which helped us reason about pathing, direction changes, and how AI updates over time during gameplay.
* [How Frightened Ghosts Decide Where to Go](https://www.youtube.com/watch?v=eFP0_rkjwlY) - A focused explanation of frightened-mode behavior, showing how ghosts prioritize avoidance and movement choices when the player is able to eat them.
* [Pygame Documentation](https://www.pygame.org/docs/) - The official reference for event handling, sprite rendering, surfaces, collision detection, timing, and game loops. This documentation was essential for implementing smooth movement and reliable UI updates.

### External Audio Content
* [Pac-Man Soundtracks & Audio Archive (Khinsider)](https://downloads.khinsider.com/search?search=pacman) - A public archive of Pac-Man-related audio files and soundtrack releases, used as a reference for selecting and analyzing retro arcade music and sound effects.
* [Pac-Man Game Sound Effects - Original Soundtrack (Khinsider)](https://downloads.khinsider.com/game-soundtracks/album/pac-man-game-sound-effect-original-soundtrack-2024) - A digitally archived collection of Pac-Man sound effects and associated audio material. This source was used as a reference for the characteristic timing, tone, and synth texture of the original arcade sound design.
* [Pac-Man 256 Android/iOS Gamerip (Khinsider)](https://downloads.khinsider.com/game-soundtracks/album/pacman-256-android-ios-gamerip-2015) - A public audio archive related to the Pac-Man 256 franchise and associated sound palette, used to compare variations in arcade-era game audio and tonal treatment.
* [JR Pac-Man Arcade Gamerip (Khinsider)](https://downloads.khinsider.com/game-soundtracks/album/jr-pacman-arcade-gamerip-1983) - A retro arcade audio archive for JR Pac-Man, used as a stylistic reference for classic maze-chase-era sound patterns and chip-tune production techniques.
* [Pac-Mania Original Soundtrack (Khinsider)](https://downloads.khinsider.com/game-soundtracks/album/pac-mania-original-soundtrack-2020) - A soundtrack archive used to study the broader Pac-Man franchise sound identity and compare later arcade interpretations of the same classic gameplay aesthetic.
* [Pac-Mania Original Soundtrack (Khinsider, Alternate Archive)](https://downloads.khinsider.com/game-soundtracks/album/pac-mania-original-soundtrack-2024) - An alternate public archive of the Pac-Mania soundtrack used for stylistic reference and audio analysis during the design of the project’s retro effects.
* [ClassicGaming.cc - Pac-Man Sounds](https://classicgaming.cc/classics/pac-man/sounds) - Archive of original Pac-Man sound effects and historical audio references, used to verify the characteristic timbre and sequencing of the classic arcade effects.

### AI Usage
* **AI Usage (Gemini/ChatGPT):** AI tools were used as coding assistants and review partners to design and implement game development strategy, debug state-machine edge cases, validate logic for score/timer systems, and help refine regex-based validation and configuration parsing. They were also helpful for identifying subtle rendering and timing issues caused by platform-specific behavior and Pygame event quirks as well as integrating audio effects into the game.

### Legal Disclaimer

The audio files and sound archives used in this project were obtained from publicly available sources that distribute archival or reference recordings free of charge. Their use in this project was limited to educational, non-commercial, and demonstrative purposes and was carried out in accordance with applicable copyright law and the terms of the corresponding source platforms. This project does not claim ownership of the original sound recordings; all rights remain with their respective copyright holders. We do not distribute the original audio files as standalone assets and do not use them for commercial gain.
---