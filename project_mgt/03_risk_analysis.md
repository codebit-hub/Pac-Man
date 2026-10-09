# Risk Analysis

## 1. Purpose

This document records the main technical risks encountered while developing the Python Pac-Man game project, their impact, and the mitigation applied or recommended for verification.

## 2. Risk register

| ID | Risk | Likelihood / impact | Consequence | Mitigation and status |
|---|---|---|---|---|
| R1 | Strict MLX graphics compliance requires pixel-by-pixel shape drawing | High / High | Rendering consumes substantial CPU time and reduces the available time for game logic and input processing | Keep drawing operations as efficient as the permitted MLX API allows; avoid unnecessary redraws where permitted; profile rendering; verify that optimizations remain compliant. A significant CPU bottleneck was observed. |
| R2 | CPU lag makes movement and collision checks frame-dependent | High / High | Pac-Man may move too far between checks and pass over a pacgum without collecting it (“tunneling”) | Use a fixed-timestep accumulator and small simulation steps. The team implemented 0.016-second micro-steps as a mitigation. |
| R3 | Use of a timing API violates project/library rules | Medium / High | The game may fail compliance checks or behave inconsistently with the permitted framework | Replace `pygame.time` usage with Python's native `time.perf_counter()` and verify that no prohibited timing dependency remains in the relevant game loop. |
| R4 | Front-end and back-end integration mismatch | Medium / High | Rendering, input, game state, or timers may disagree about the current state | Maintain separate development branches, coordinate interface changes, integrate shared files deliberately, and run end-to-end smoke tests. |
| R5 | Invalid or inconsistent configuration data | Medium / High | The game may fail at startup or use invalid level/gameplay settings | Validate JSON structure, required fields, types, and acceptable value ranges; handle invalid files predictably. Include malformed-input tests in the acceptance plan. |
| R6 | Feature changes introduce regressions late in the schedule | Medium / Medium | Previously working gameplay may break near the deadline | Use focused regression tests after changes to the game loop, levels, pacgums, cheat mode, high scores, and UI. Keep the six-day evaluation buffer for preparation and fixes. |

Likelihood and impact are qualitative assessments for planning, not measured statistical values.

## 3. Key risk: MLX rendering bottleneck

### Cause

Strict MLX graphics compliance required shapes to be drawn pixel-by-pixel. This created a large number of drawing operations and became a significant CPU bottleneck.

### Impact

- Reduced rendering and update performance.
- Increased timing variability under load.
- Made gameplay behavior more sensitive to how often the simulation loop ran.
- Exposed a collision accuracy issue: at high speeds, Pac-Man could skip over a pacgum between checks.

### Mitigation

1. Keep the rendering implementation within the required MLX rules.
2. Separate simulation timing from rendering frequency where the architecture allows.
3. Use bounded, small simulation steps so movement and collision checks do not depend entirely on a slow rendered frame.
4. Avoid unnecessary rendering work where the permitted API and project rules allow it.
5. Test collision accuracy under CPU load and at higher movement speeds.

The team implemented a fixed-timestep accumulator using 0.016-second micro-steps to mitigate the tunneling symptom. This improves the granularity of simulation updates; it should still be tested against the project's actual movement and collision implementation.

## 4. Risk monitoring and residual risk

The fixed-step approach mitigates frame-dependent movement, but it does not by itself guarantee that every collision case is correct. Residual risk remains if:

- The movement distance within a simulation step is still too large for the collision geometry.
- Collision checks do not cover the full path between the previous and next positions.
- The simulation cannot catch up safely after a long stall.
- Rendering continues to consume so much CPU that input responsiveness becomes unacceptable.

Acceptance testing should therefore include normal and high-speed movement, narrow targets, different frame rates or artificial delays where feasible, and repeated collection attempts near pacgums.

## 5. Ownership and follow-up

- **Back-end / game logic:** Fixed-step simulation, movement, collision, timers, configuration validation, and game-state correctness.
- **Front-end / rendering:** MLX-compliant drawing efficiency, renderer behavior, UI feedback, and audio integration.
- **Shared:** End-to-end performance, integration regressions, and evaluation readiness.

