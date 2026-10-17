<div align="center">
  <img src="https://img.shields.io/badge/Grade-100%25%2F100%25-2ecc71?style=for-the-badge&logo=check-circle&logoColor=white" alt="Grade 100%/100%" />
  <img src="https://img.shields.io/badge/Completed-13.10.2026-f7b801?style=for-the-badge" alt="Completed 13.10.2026" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/Mypy%20%2F%20Flake8-passing-00b894?style=for-the-badge&logo=python&logoColor=white" alt="Mypy/Flake8" />
  <img src="https://img.shields.io/badge/MiniLibX-Ready-8e44ad?style=for-the-badge" alt="MiniLibX" />
  <img src="https://img.shields.io/badge/PyGame-Ready-ff6b35?style=for-the-badge&logo=pygame&logoColor=white" alt="PyGame" />
</div>

*This project has been created as part of the 42 curriculum by dporhomo, vokotera.*

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

### How to Download and Play the Pre-Compiled Build

A pre-compiled Linux build has been uploaded as an unlisted, restricted project on Itch.io.

1. **Access the Build:** Navigate to the secret URL provided for the evaluation: `https://codebit.itch.io/pac-man?secret=sOjS0gzLesg7acxiciNWgciemk`
2. **Download:** Click the "Download" button to save the `pac-man-linux.zip` file to your computer.
3. **Extract:** Unzip the downloaded file:
```bash
unzip pac-man-final.zip -d pac-man-game
```


4. **Launch:** Navigate into the extracted directory and run the standalone executable:
```bash
cd pac-man-game/pac-man/
./pac-man
```


*(Note: The executable automatically discovers the bundled `config.json` and assets; no command-line arguments are required.
You can modify the _internal/config.json to change game behaviour and settings. Then run `./pac-man config.json`.).*

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

### Front-End Features & Trade-Offs:
* **Strict MLX Software Rendering vs. Hardware Acceleration (CPU Bottleneck):**
  * *Constraint:* The 42 subject mandates that *every graphical library function used must have a direct equivalent in the MiniLibX (MLX) library (`mlx.h`)*. High-level Pygame drawing primitives (`pygame.draw.rect`, `pygame.draw.circle`, `pygame.draw.line`, `pygame.draw.polygon`) have no equivalent in MLX, which only provides single-pixel manipulation (`mlx_pixel_put`) and direct image blitting (`mlx_put_image_to_window`).
  * *Trade-off & Solution:* We completely eliminated `pygame.draw` and implemented a dedicated `MLXUtils` class. All geometry is drawn via custom software loops using `Surface.set_at((x, y), color)`:
    * Rectangles & Walls (`MLXUtils.draw_rect`): Nested loops with strict boundary clipping (`min`, `max`) against window boundaries.
    * Dots & Pellets (`MLXUtils.draw_circle`): Bounding-box iteration evaluating the Pythagorean circle equation ($x^2 + y^2 \le r^2$).
    * Lines (`MLXUtils.draw_line`): Integer-only Bresenham's line algorithm with configurable width offset.
    * Triangles & Pointers (`MLXUtils.draw_triangle`): Bounding-box reduction with half-plane 2D cross-product edge tests (`sign()`).
  * *Compromise:* Executing pixel math in Python bytecode introduces an inherent CPU bottleneck. While modern GPUs handle geometric primitives virtually for free, our pure CPU approach strictly guarantees algorithmic authenticity and 100% compliance with 42 curriculum standards.

* **Asset Scaling Strategy: Eager Caching vs. Real-Time Nearest-Neighbor:**
  * *Constraint:* MLX lacks an image-scaling routine (such as `pygame.transform.scale`).
  * *Trade-off & Solution:* We authored `MLXUtils.scale_image` using manual nearest-neighbor interpolation (`src_x = min(int(dst_x * src_w / new_w), src_w - 1)`). However, running this software loop per frame for dozens of animated sprites would drop framerates below playable thresholds.
  * *Compromise:* We implemented an **eager asset caching architecture**. All spritesheets, player animations, ghost direction frames, and UI icons are scaled once via `MLXUtils` at grid initialization and cached in memory. Runtime frames exclusively use basic blit operations (`mlx_put_image_to_window` equivalent), preserving both MLX mathematical compliance and a rock-solid 60 FPS.

* **Color Modulation & UI Feedback (`colorize_icon` vs. SDL Blend Flags):**
  * *Constraint:* Hardware blend modes (e.g. `pygame.BLEND_RGB_ADD`) do not exist in MLX.
  * *Trade-off & Solution:* In `MLXUtils.colorize_icon`, button hover highlights, menu selections, and entity flashing are implemented by directly inspecting raw surface pixel RGBA channels, ignoring transparent pixels (`a > 0`), and arithmetically shifting RGB values with explicit 8-bit clamping (`min(255, val + add)`). This replicates direct memory buffer manipulation (`mlx_get_data_addr`).

* **Dynamic Window Geometry vs. Fixed-Aspect Retro Tile Grid:**
  * *Constraint:* The game dynamically loads levels with variable grid dimensions (e.g., 15×15 up to 30×30 cells, expanded to $(2W + 1) \times (2H + 1)$ by the maze algorithm).
  * *Trade-off & Solution:* Rather than stretching sprites or letterboxing with uneven borders, the window dynamically sizes itself to the exact grid width and height (`tile_size = 24px`), appending a standardized vertical offset for the telemetry HUD. This ensures crisp pixel art without non-uniform scaling or visual distortion.

* **Decoupled Simulation: Fixed Timestep Accumulator:**
  * *Constraint:* CPU-heavy software rendering creates timing variance. Under standard variable `delta_time`, moving at high speeds or suffering a CPU spike caused Pac-Man to jump multiple tiles in a single frame, skipping pellets (the "tunneling" bug).
  * *Trade-off & Solution:* Front-end rendering is completely decoupled from physics simulation via a **Fixed Timestep Accumulator** (`FIXED_DT = 0.016s`). Render lag never influences collision detection or gameplay fairness.

* **Audio System Graceful Degradation:**
  * *Constraint:* 42 evaluation environments (headless clusters, SSH tunnels, WSL, VMs without audio sinks) often crash when initializing sound cards.
  * *Trade-off & Solution:* The `AudioManager` wraps all mixer initialization and playback in safe exception guards. If sound hardware is missing or fails, the game falls back silently to a no-op state without crashing, while still exposing in-game mute options in the pause menu.

* **HUD Telemetry & Evaluation Feedback:**
  * The persistent bottom HUD tracks Level, Score, Lives, and remaining Level Time. In `"evaluation"` mode, it dynamically displays real-time ghost wave states (`MODE: SCATTER / CHASE / FLEE`), giving evaluators direct visual verification of the underlying state machine.

**MLX Library Compliance:**
The project was explicitly designed to comply with the constraint that *any graphical library function used must have a direct equivalent in the MiniLibX (MLX) library*. Because Pygame's built-in drawing primitives have no equivalent in MLX (which only provides pixel rendering), we implemented a custom `MLXUtils` class. Furthermore, standard Pygame timing functions (`pygame.time.Clock`, `get_ticks()`) were entirely stripped from the backend and replaced with Python's native `time.perf_counter()` to strictly mirror standard C-library time management.

| Game Implementation (Python/Pygame) | MLX Equivalent (`mlx.h`) | Description |
|-------------------------------------|--------------------------|-------------|
| `Surface.set_at((x, y), color)` inside nested `for` loops (`MLXUtils.draw_rect`, `draw_circle`) | `mlx_pixel_put` | Used to draw rectangles, circles, pellets, and borders pixel by pixel. |
| Bresenham's Line Algorithm via `set_at()` (`MLXUtils.draw_line`) | `mlx_pixel_put` | Replicates line drawing without native vector graphics. |
| Geometric polygon fill via `set_at()` (`MLXUtils.draw_triangle`) | `mlx_pixel_put` | Replicates triangle drawing pixel by pixel. |
| Nearest-neighbor scaling via `set_at()` (`MLXUtils.scale_image`) | `mlx_pixel_put` / image buffer loop | Replicates image scaling using custom software interpolation. |
| `Surface.get_at((x, y))` / `set_at` looping (`MLXUtils.colorize_icon`) | `mlx_get_data_addr` / memory buffer modification | Replicates pixel-level color blending and alpha manipulation without using `BLEND_RGB_ADD`. |
| Native Python `time.perf_counter()` | `<sys/time.h>` / `gettimeofday` | Replaces `pygame.time` to ensure time-management relies on standard OS libraries, not the graphical library. |
| Basic `blit` operations | `mlx_put_image_to_window` | Standard 2D image drawing. |


### Back-End Features & Trade-Offs:
* **Robust Configuration Parsing & Graceful Fallbacks:**
  * *Constraint:* The game must not crash due to user error in the configuration file, such as missing files, bad types, or corrupted data.
  * *Trade-off & Solution:* We implemented a highly defensive `ConfigManager`. Instead of simply crashing when `config.json` is missing, the script catches the `FileNotFoundError` and seamlessly boots using a hardcoded `_defaults` dictionary. We also bypassed standard Python JSON parsing limitations by injecting a custom `object_pairs_hook` into `json.loads()`. This intercepts duplicate JSON keys during the read phase and safely clamps them to predefined default values, preventing silent configuration overwrites.

* **Decoupled State Machine Architecture:**
  * *Implementation:* The game flow is managed by a central `Application` class acting as a finite state machine (`MENU`, `PLAYING`, `PAUSE`, `NAME_INPUT`, `HIGHSCORES`). The backend logic (`GameState`) handles all entity updates, wave timers, and score aggregation completely independently of the front-end graphics, ensuring that UI lag never impacts the underlying game math.

* **Authentic Ghost AI & Time Management:**
  * *Implementation:* The backend replicates canonical arcade AI waves (Scatter, Chase, and Flee modes). To maintain strict MLX compliance, all backend timing loops and wave transitions are driven by standard OS-level libraries (`time.perf_counter()`) rather than graphical library clock ticks.

* **Deterministic vs. Procedural Maze Generation:**
  * *Implementation:* The backend wraps the external `A-Maze-ing` package via `MazeLoader`.
  * *Trade-off & Solution:* To satisfy the need for both predictable evaluation and replayability, the logic explicitly feeds the configuration `seed` (default: 42) into Level 1 to guarantee a deterministic layout. For all subsequent levels, the backend drops the seed and utilizes `random.randint`, ensuring infinite procedural generation while dynamically calculating valid pacgum capacities and safe entity spawn coordinates (e.g., placing Pinky precisely in the top-left corner).

* **Evaluation "Cheat" Mode Isolation:**
  * *Implementation:* To aid peers during the 42 evaluation process without compromising the integrity of the base game, we introduced a strict `game_mode` toggle in the config. Setting this to `"evaluation"` unlocks a developer pause menu that allows real-time dynamic speed scaling, invincibility toggles, and instant level skipping.

* **Lightweight Persistence (JSON vs. Databases):**
  * *Trade-off & Solution:* For the top-10 leaderboard, we traded the robustness of a relational database (like SQLite) for a lightweight `highscore.json` implementation. This removes heavy dependencies and keeps the save file human-readable. To mitigate the risk of file injection, the backend aggressively validates leaderboard reads and utilizes strict Regex sanitization on player names (clamping to 10 alphanumeric characters) before writing to the disk.

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

We utilized an Agile approach with the extensive application of GitHub features.

* **Team Organization:** The project was developed by two teammates. `vokotera` developed the front-end architecture and MLX-compliant rendering systems, while `dporhomo` focused on the back-end logic, state machine, physics, entity AI and overall project management.
* **Branching Strategy:** We worked in separate feature branches, predominantly `Front-end-dev` and `Back-end-dev`. We gradually worked in our respective branches and pushed them to Git frequently.
* **Pull Requests & Code Review:** Stable features were merged into the `main` branch solely through Pull Requests. This allowed us to validate changes, share our work, review progress in incremental steps, and ensure backup points.
* **Task Tracking:** We used GitHub Issues as tickets to track bugs, assign specific feature modules, and monitor progress across a 4-week lifecycle.
* **Timeline:** We allocated exactly 4 weeks to complete the full scope of this project. Core features were completed by Day 22, reserving the final 6 days strictly for evaluation prep, bug fixing, and compliance audits.

A dedicated directory containing evidence of our project management methodology (including timelines, tracking boards, risk analysis, and team organization) can be found in the [`project_mgt/`](./project_mgt/01_team_organization.md) folder.

* **01_team_organization.md**: Details the front-end/back-end split between vokotera and dporhomo, and how you communicated (GitHub discussions, daily syncs).

* **02_timeline_and_progress.md**: A retro-fitted 4-week timeline based on your closed GitHub issues. Week 1: Setup/Makefile. Week 2: Logic/Grid/Maze. Week 3: Front-end rendering/UI. Week 4: Bug fixing/MLX compliance.

* **03_risk_analysis.md**: Highlights the MLX CPU bottleneck risk, the tunneling bug, and the mitigation strategies (MLXUtils + Fixed Timestep).

* **04_blocking_points.md**: Details the realization that pygame.time violated MLX rules and how it was surgically removed and replaced with standard Python time.

* **05_acceptance_test_plan.md**: A checklist of the edge cases you tested (Evaluation mode speeds, JSON config corruption, level scaling).

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
