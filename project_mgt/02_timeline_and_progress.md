# Timeline and Progress

## 1. Summary

The project was planned over a four-week window. Implementation was completed in 22 days, leaving six days for evaluation preparation.

- **Issues closed:** 20
- **Delivery status:** Implementation completed ahead of the end of the four-week window
- **Remaining buffer:** Six days reserved for evaluation preparation

The timeline below groups the supplied issue list by week. It records the reported sequence and scope; it does not claim exact calendar dates or issue-by-issue durations.

**Completed**
[Issue #2](https://github.com/codebit-hub/Pac-Man/issues/2)

## 2. Weekly breakdown

### Week 1 — Project setup and configuration

**Focus:** Establish the development foundation and configuration mechanism.

Issues:
- Backend Makefile update
- Back-end: create configuration file

**Progress outcome:** Initial project setup and configuration work were addressed, providing a foundation for later gameplay features.

**Dependencies and risks:** Configuration handling needed to be reliable because later game behavior could depend on values loaded from a file.

**Completed**
[Issue #3](https://github.com/codebit-hub/Pac-Man/issues/3)

**Completed**
[Pull Request #16](https://github.com/codebit-hub/Pac-Man/pull/16)

### Week 2 — Core back-end systems

**Focus:** Build the main game-domain modules.

Issues:
- Back-end: `src/player`
- Back-end: `maze_loader`
- Back-end: `game_state`
- Back-end: `highscore`
- Back-end: `ghost`

**Progress outcome:** The core modules for player behavior, maze loading, game state, high scores, and ghosts were implemented.

**Dependencies and risks:** These modules interact during the game loop. Integration testing was important to catch mismatches between state updates, collision behavior, maze data, and rendering.

**Completed**
[Issue #5](https://github.com/codebit-hub/Pac-Man/issues/5),
[Issue #6](https://github.com/codebit-hub/Pac-Man/issues/6),
[Issue #7](https://github.com/codebit-hub/Pac-Man/issues/7),
[Issue #8](https://github.com/codebit-hub/Pac-Man/issues/8),
[Issue #9](https://github.com/codebit-hub/Pac-Man/issues/9)

**Completed**
[Pull Request #17](https://github.com/codebit-hub/Pac-Man/pull/17),
[Pull Request #18](https://github.com/codebit-hub/Pac-Man/pull/18),
[Pull Request #19](https://github.com/codebit-hub/Pac-Man/pull/19),
[Pull Request #20](https://github.com/codebit-hub/Pac-Man/pull/20)

### Week 3 — Gameplay rules and scaling

**Focus:** Add rules that make gameplay configurable and progressively challenging.

Issues:
- Back-end: introduce level difficulty scaling
- Back-end: validate pacgums
- Back-end: make ghost color random
- Back-end: specify levels

**Progress outcome:** Work expanded the core game with level specification, difficulty progression, pacgum validation, and randomized ghost colors.

**Dependencies and risks:** Randomized presentation and scaling needed to remain compatible with the level configuration and game-state logic. Pacgum validation was especially important for reliable collection and scoring.

**Completed**
[Issue #23](https://github.com/codebit-hub/Pac-Man/issues/23),
[Issue #24](https://github.com/codebit-hub/Pac-Man/issues/24),
[Issue #25](https://github.com/codebit-hub/Pac-Man/issues/25),
[Issue #26](https://github.com/codebit-hub/Pac-Man/issues/26),
[Issue #27](https://github.com/codebit-hub/Pac-Man/issues/27),
[Issue #28](https://github.com/codebit-hub/Pac-Man/issues/28),
[Issue #29](https://github.com/codebit-hub/Pac-Man/issues/29)

**Completed**
[Pull Request #21](https://github.com/codebit-hub/Pac-Man/pull/21)


### Week 4 — UI, integration, and final features

**Focus:** Complete presentation, shared files, and remaining gameplay behavior.

Issues:
- Front-end: `src/ui` (menu, HUD, renderer, audio)
- Shared files: `pac_man.py`, `README`
- Back-end: check game loop/timers
- Back-end: create cheat mode
- Back-end: create high-score name specification

**Progress outcome:** The UI and audio work were integrated with the game logic. Shared project files and remaining timer, cheat-mode, and high-score-name behavior were addressed.

**Dependencies and risks:** The renderer and game loop were closely coupled through frame timing. Strict graphics constraints created a CPU bottleneck, while timing behavior affected movement and collision accuracy. These issues required targeted engineering work during integration.

**Completed**
[Issue #10](https://github.com/codebit-hub/Pac-Man/issues/10),
[Issue #11](https://github.com/codebit-hub/Pac-Man/issues/11),
[Issue #12](https://github.com/codebit-hub/Pac-Man/issues/12),
[Issue #13](https://github.com/codebit-hub/Pac-Man/issues/13),
[Issue #14](https://github.com/codebit-hub/Pac-Man/issues/14)

**Completed**
[Pull Request #22](https://github.com/codebit-hub/Pac-Man/pull/22),
[Pull Request #30](https://github.com/codebit-hub/Pac-Man/pull/30)

## 3. Milestones

| Milestone | Evidence / outcome |
|---|---|
| Foundation ready | Makefile and configuration-file issues closed |
| Core game logic implemented | Player, maze loader, game state, high score, and ghost issues closed |
| Gameplay rules added | Difficulty scaling, pacgum validation, random ghost color, and level specification issues closed |
| Integrated game completed | UI, shared files, timers/game loop, cheat mode, and high-score name issues closed |
| Evaluation preparation | Six days remained after implementation was completed on day 22 |

## 4. Progress management

GitHub Issues and pull requests were used to make the work visible and track completion. The two development branches separated the primary front-end and back-end areas, while shared files and integration-sensitive changes required coordination.

The schedule was managed against the four-week deadline, with the final six days retained as a buffer for evaluation preparation rather than planned feature development.

**Completed**
[Issue #15](https://github.com/codebit-hub/Pac-Man/issues/15)

## 5. Reporting limitations

This document is based on the supplied issue titles and weekly grouping. Exact start dates, assignees for individual issues, pull-request identifiers, review durations, and issue closure timestamps were not maintained.
