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

#### 'How-to-Play' Instructions

Alongside the executable in the extracted directory, you will find a 'HOW_TO_PLAY.txt' file that you can open for a quick reference on controls, scoring, and gameplay mechanics.

---

## Configuration

The game logic relies entirely on a mandatory `config.json` file. The backend parses this securely, preventing silent failures by catching errors (e.g., missing files, booleans incorrectly parsed as integers) and safely clamping or reverting to defaults.

**Key Structure & Default Behaviors:**
* `game_mode` (default: `"game"`): Accepts `"game"` or `"evaluation"`. Evaluation mode enables in-game cheats via the Pause menu (invincibility, speed tuning, level skipping).
* `highscore_filename` (default: `"highscore.json"`): Standardized path for persistent JSON saving.
* `levels` (default: `12`): Total number of levels before triggering the Victory state.
* `level` (default: `[{"width": 15, "height": 15}]`): Array defining the grid size of the levels.
* `lives` (default: `3`): Number of lives the player starts with.
* `pacgum` (default: `42`): Seed/Configuration for pacgum distribution.
* `points_per_pacgum` (default: `10`), `points_per_super_pacgum` (default: `50`), `points_per_ghost` (default: `200`): Scoring values for various entities.
* `seed` (default: `42`): Integer used to generate Level 1 predictably.
* `level_max_time` (default: `90`): Time limit per level in seconds.
* `ghost_behavior_random` (default: `false`): If true, dynamically shuffles ghost spawn corners and visual colors upon initialization.

---

## Highscore

The project utilizes a persistent Highscore system managed by the `HighScoreManager` class, tracking the Top 10 players locally.

* **Implementation Choice:** It relies on an external `highscore.json` file. JSON was chosen because it natively serializes Python dictionaries, removing the need for a heavy external database library while keeping the save file human-readable.
* **Robustness & Accuracy:** The backend aggressively validates the data. If the JSON is manually corrupted, missing, or injected with negative scores/invalid types, the system safely catches the `JSONDecodeError` or `OSError` and falls back to an empty leaderboard rather than crashing.
* **Player Names:** Names are sanitized via Regex to enforce alphanumeric characters and spaces only, explicitly clamping the length to a maximum of 10 characters. Empty inputs default to `"ANONYMOUS"`.

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

**Front-End Features & Trade-Offs:**
* **Retro UI & Animations:** The front-end renders a fully responsive grid matching the configuration file. It features animated menus, animated entity sprites using a spritesheet, and a persistent bottom HUD (Score, Lives, Level, Timer).
<<<<<<< HEAD
* **Trade-offs:** We actively traded Pygame's hardware-accelerated shape rendering (`pygame.draw`) for custom software-rendering loops (`MLXUtils`) to strictly comply with the MLX requirement. While this introduces a CPU bottleneck, it guarantees algorithmic authenticity. 
=======
* **Trade-offs:** We actively traded Pygame's hardware-accelerated shape rendering (`pygame.draw`) for custom software-rendering loops (`MLXUtils`) to strictly comply with the MLX requirement. While this introduces a CPU bottleneck, it guarantees algorithmic authenticity.
>>>>>>> origin/MLX-Backend

**Fixed Timestep & Collision Consistency:**
The CPU-heavy pixel-by-pixel rendering inherently introduces artificial frame lag. Using a standard frame-independent `delta_time` caused high-speed entities to teleport across multiple tiles in a single frame, phasing through pacgums and missing collisions. To guarantee exact logic execution at any dynamic speed (from 0 to 10 in evaluation mode), the engine implements a **Fixed Timestep with an Accumulator**. This architecture completely decouples the physical rendering loop from the backend physics loop. It accumulates real-world frame lag and processes the game logic in strict 0.016-second micro-steps before drawing to the screen. This ensures 100% collision accuracy and consistent rendering behavior.

**MLX Library Compliance:**
<<<<<<< HEAD
The project was explicitly designed to comply with the constraint that *any graphical library function used must have a direct equivalent in the MiniLibX (MLX) library*. Because Pygame's built-in drawing primitives (like `pygame.draw.rect` or `pygame.draw.circle`) have no equivalent in MLX (which only provides pixel rendering), we implemented a custom `MLXUtils` class. All shapes and image processing were achieved using manual pixel-by-pixel loops.
=======
The project was explicitly designed to comply with the constraint that *any graphical library function used must have a direct equivalent in the MiniLibX (MLX) library*. Because Pygame's built-in drawing primitives have no equivalent in MLX (which only provides pixel rendering), we implemented a custom `MLXUtils` class. Furthermore, standard Pygame timing functions (`pygame.time.Clock`, `get_ticks()`) were entirely stripped from the backend and replaced with Python's native `time.perf_counter()` to strictly mirror standard C-library time management.
>>>>>>> origin/MLX-Backend

| Game Implementation (Python/Pygame) | MLX Equivalent (`mlx.h`) | Description |
|-------------------------------------|--------------------------|-------------|
| `Surface.set_at((x, y), color)` inside nested `for` loops (`MLXUtils.draw_rect`, `draw_circle`) | `mlx_pixel_put` | Used to draw rectangles, circles, and borders pixel by pixel. |
| Bresenham's Line Algorithm via `set_at()` (`MLXUtils.draw_line`) | `mlx_pixel_put` | Replicates line drawing without native vector graphics. |
| Geometric polygon fill via `set_at()` (`MLXUtils.draw_triangle`) | `mlx_pixel_put` | Replicates triangle drawing pixel by pixel. |
<<<<<<< HEAD
| `Surface.get_at((x, y))` / `set_at` looping (`MLXUtils.colorize_icon`) | `mlx_get_data_addr` / memory buffer modification | Replicates pixel-level color blending and alpha manipulation without using `BLEND_RGB_ADD`. |
| Basic `blit` operations | `mlx_put_image_to_window` | Standard 2D image drawing. |

This strictly manual pixel-manipulation approach guarantees that the implementation is 100% compatible with the MLX standard.
=======
| Native Python `time.perf_counter()` | `<sys/time.h>` / `gettimeofday` | Replaces `pygame.time` to ensure time-management relies on standard OS libraries, not the graphical library. |
| Basic `blit` operations | `mlx_put_image_to_window` | Standard 2D image drawing. |
>>>>>>> origin/MLX-Backend
---

## General Software Architecture

The software architecture completely decouples the backend state and logic from the front-end rendering module.

* **`pac-man.py`**: The safe CLI entry point that intercepts tracebacks and handles execution arguments.
* **`src/main.py` (`Application`)**: The central hub that routes inputs, handles state transitions, runs the fixed-timestep physics accumulator, and manages the Pygame event loop.
* **`src/config.py`**: Independent module dedicated strictly to loading, validating, and applying `config.json` rules safely.
* **`src/highscore.py`**: Independent module responsible for safely parsing, sanitizing, sorting, and saving data to `highscore.json`.
* **`src/game_state.py`**: The logical referee tracking lives, points, level transitions, timers (e.g., Flee mode, Scatter/Chase wave switching), and checking victory/loss conditions.
* **`src/player.py`**: OOP representation of Pac-Man, tracking input direction queues, movement logic, and exact sub-tile position.
* **`src/ghost.py`**: OOP representation of ghosts containing distinct behaviors (Scatter, Chase, Flee, Eaten), internal pathfinding, and dynamic speed math.
* **`src/maze_loader.py`**: An abstraction layer specifically for importing and interacting with the external `A-Maze-ing` package to generate grid maps.
* **`src/renderer.py` (`Render` / `MLXUtils`)**: The core front-end module. Handles all Pygame surface drawing, spritesheet extraction, and contains the `MLXUtils` class which executes MLX-compliant pixel-by-pixel rendering math.
* **`src/menu.py`**: Manages the Main Menu state, including retro animations, title screens, and instruction overlays.
* **`src/pause_menu.py`**: Handles the Pause overlay and the robust Evaluation/Cheat mode interface.
* **`src/highscore_screen.py`**: Manages the Game Over / Victory screens, rendering the leaderboard and handling interactive user text input.
* **`src/ui_config.py`**: Defines reusable front-end design tokens (fonts, colors, standardized panel backgrounds).
* **`src/audio.py`**: Handles sound loading, volume configuration, BGM toggles, and sound-effect playback.

---

## Project Management

<<<<<<< HEAD
A dedicated directory containing evidence of our project management methodology (including timelines, tracking boards, risk analysis, and team organization) can be found in the [`project_management/`](./project_management/) folder.

We utilized an Agile approach with the extensive application of GitHub features. 

* **Team Organization:** The project was developed by two teammates. `vokatera` developed the front-end architecture and rendering systems, while `dporhomo` focused on the back-end logic, state machine, and entity AI.
* **Branching Strategy:** We worked in separate feature branches, predominantly `Front-end-dev` and `Back-end-dev`. We gradually worked in our respective branches and pushed them to Git frequently.
* **Pull Requests & Code Review:** Stable features were merged into the `main` branch solely through Pull Requests. This allowed us to validate changes, share our work, review progress in incremental steps, and ensure backup points.
* **Task Tracking:** We used GitHub Issues as tickets to track bugs, assign specific feature modules, and monitor progress.
* **Communication:** GitHub Discussions were leveraged to align on technical decisions alongside our daily coding check-ins.
* **Timeline:** We allocated exactly 4 weeks to complete the full scope of this project, successfully fulfilling the initial plan.
=======
A dedicated directory containing evidence of our project management methodology (including timelines, tracking boards, risk analysis, and team organization) can be found in the [`project_mgt/`](./project_mgt/) folder.

* **01_team_organization.md**: Details the front-end/back-end split between vokatera and dporhomo, and how you communicated (GitHub discussions, daily syncs).
>>>>>>> origin/MLX-Backend

* **02_timeline_and_progress.md**: A retro-fitted 4-week timeline based on your closed GitHub issues. Week 1: Setup/Makefile. Week 2: Logic/Grid/Maze. Week 3: Front-end rendering/UI. Week 4: Bug fixing/MLX compliance.

* **03_risk_analysis.md**: Highlights the MLX CPU bottleneck risk, the tunneling bug, and the mitigation strategies (MLXUtils + Fixed Timestep).

* **04_blocking_points.md**: Details the realization that pygame.time violated MLX rules and how it was surgically removed and replaced with standard Python time.

* **05_acceptance_test_plan.md**: A checklist of the edge cases you tested (Evaluation mode speeds, JSON config corruption, level scaling).


### Overview
We utilized an Agile approach with the extensive application of GitHub features.

* **Team Organization:** The project was developed by two teammates. `vokatera` developed the front-end architecture and MLX-compliant rendering systems, while `dporhomo` focused on the back-end logic, state machine, physics, and entity AI.
* **Branching Strategy:** We worked in separate feature branches, predominantly `Front-end-dev` and `Back-end-dev`. We gradually worked in our respective branches and pushed them to Git frequently.
* **Pull Requests & Code Review:** Stable features were merged into the `main` branch solely through Pull Requests. This allowed us to validate changes, share our work, review progress in incremental steps, and ensure backup points.
* **Task Tracking:** We used GitHub Issues as tickets to track bugs, assign specific feature modules, and monitor progress across a 4-week lifecycle.
* **Timeline:** We allocated exactly 4 weeks to complete the full scope of this project. Core features were completed by Day 22, reserving the final 6 days strictly for evaluation prep, bug fixing, and compliance audits.

---

## Resources

### Core Technologies
* [MiniLibX (MLX)](https://github.com/42Paris/minilibx-linux) - A simple X-Window (X11) programming API provided by 42, used by students to render graphics pixel by pixel. Its strict limitations (drawing only via `mlx_pixel_put` and images) heavily influenced this project's custom `MLXUtils` software-rendering constraints.

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

* **Disclaimer:** The audio files and sound archives used in this project were obtained from publicly available sources that distribute archival or reference recordings free of charge. Their use in this project was limited to educational, non-commercial, and demonstrative purposes and was carried out in accordance with applicable copyright law and the terms of the corresponding source platforms. This project does not claim ownership of the original sound recordings; all rights remain with their respective copyright holders. We do not distribute the original audio files as standalone assets and do not use them for commercial gain.

---
