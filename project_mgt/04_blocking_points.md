# Blocking Points and Technical Resolutions

## 1. Overview

Two important blocking points affected the implementation:

1. CPU-intensive MLX rendering contributed to a collision “tunneling” bug in which Pac-Man could skip pacgums at high speeds.
2. The team identified that `pygame.time` violated the project's MLX-related rules and refactored timing to use Python's native `time.perf_counter()`.

These problems affected gameplay correctness and compliance, so they required changes beyond adding new features.

## 2. Blocking point A — Pacgum tunneling under CPU load

### Observed behavior

When Pac-Man moved quickly, he could pass over a pacgum without collecting it. The issue became apparent in the context of slow rendering and CPU load.

### Technical explanation

A frame-dependent loop can move an object a relatively large distance between collision checks. If the collision test checks only the new position, the object may cross a small target between two checks without ever overlapping it at a sampled position. This is commonly called *tunneling*.

Pixel-by-pixel MLX drawing increased CPU load. Under lag, the time between effective updates could grow, making movement and collision outcomes less reliable if simulation progress was tied directly to rendered frames.

### Mitigation implemented

The team introduced a **Fixed Timestep Accumulator** and used **0.016-second micro-steps** for simulation updates.

Conceptually, the loop accumulates elapsed real time and advances the game simulation in fixed-size increments:

```python
FIXED_DT = 0.016
accumulator += elapsed_time

while accumulator >= FIXED_DT:
    update_game(FIXED_DT)
    check_collisions()
    accumulator -= FIXED_DT
```

This is an illustrative description of the approach, not a claim that the repository uses this exact code or function names. The actual implementation should remain the source of truth.

### Why this helps

- Simulation updates use a consistent time step instead of one variable step per rendered frame.
- Movement and collision checks occur in smaller increments.
- A large elapsed interval can be processed as multiple simulation steps, reducing the chance of passing over a small target unnoticed.

### Remaining caveats

A fixed timestep is not a universal guarantee against tunneling. Correctness still depends on movement distance per step, collision geometry, and whether collision checks run at each relevant step.

### Verification

- Reproduce the bug by moving across a pacgum at the highest permitted speed.
- Repeat with normal rendering and under induced CPU load if the test environment allows it.
- Verify that the pacgum is collected exactly once and that score/state changes occur correctly.
- Check that walls and other collision boundaries remain reliable.
- Confirm that the game does not enter an excessive catch-up loop after a stall.

**Verification was completed successfully.**

## 3. Blocking point B — `pygame.time` compliance

### Problem

The team identified that use of `pygame.time` violated the project's MLX-related rules. Leaving it in place risked non-compliance even if the timer worked functionally.

### Resolution implemented

The backend timing logic was refactored to use Python's native `time.perf_counter()`.

`perf_counter()` provides a high-resolution monotonic performance counter suitable for measuring elapsed time. The usual pattern is to take a starting reading and subtract it from a later reading:

```python
import time

previous_time = time.perf_counter()

while running:
    current_time = time.perf_counter()
    elapsed_time = current_time - previous_time
    previous_time = current_time

    # Feed elapsed_time into the permitted game-loop/update logic.
```

This snippet illustrates the timing pattern; adapt it to the actual project loop and its permitted APIs.

### Why this helps

- Removes the identified dependency on `pygame.time`.
- Uses Python's standard library to measure elapsed time.
- Supports the fixed-timestep accumulator by providing elapsed-time measurements independently of the renderer.

### Verification

- Search the relevant source files for remaining `pygame.time` references.
- Start the game and confirm that timers and level transitions still work.
- Test the final three-second warning behavior, if implemented, and confirm that the timer reaches zero reliably.
- Check that the game loop remains responsive and that elapsed time is not accidentally counted twice or discarded.
- Confirm compliance with the project's exact MLX/library restrictions.

**Verification was completed successfully.**

## 4. Lessons learned

- Rendering performance can become a gameplay correctness issue, not just a visual-quality issue.
- Simulation updates should be designed to remain stable when rendering slows down.
- Collision tests need to consider the path travelled between updates, especially for small targets and high speeds.
- Compliance constraints should be checked early, because replacing a timing mechanism late can affect the whole game loop.
- After a low-level timing change, regression testing should cover movement, collisions, level transitions, timers, and game-over behavior.
