# Acceptance Test Plan

## 1. Purpose and scope

This plan defines practical acceptance checks for the Python Pac-Man game project, with emphasis on:

- JSON configuration validation.
- Evaluation-mode cheat toggles.
- Collision accuracy, including the pacgum tunneling issue.
- Timing and game-loop regression checks after replacing `pygame.time` with `time.perf_counter()`.

## 2. Test environment and prerequisites

Record the following before testing:

- Commit or release identifier: `6836d03 Corrected renderer, menus, ui_config, solves #10, #11, #12`
- Operating system / environment: `Ubuntu 22.04.5 LTS/Python 3.13.1`
- MLX/runtime version required by the project: `MinilibX, a simple X-Window (X11R6)`
- Tester and date: `dporhomo Oct 9, 2026`
- Configuration file used: `config.json`

## 3. Result recording

Use these status values:

- **Not run** — test has not yet been executed.
- **Pass** — actual result matches the expected result.
- **Fail** — actual result differs from the expected result.
- **Blocked** — the test could not be executed; record why.

## 4. JSON configuration validation

| ID | Test / input | Steps | Expected result | Status |
|---|---|---|---|---|
| CFG-01 | Valid configuration | Launch with a known-good JSON configuration containing all required fields and valid values. | Configuration loads successfully and the game starts with the specified settings. | **Passed** |
| CFG-02 | Missing configuration file | Temporarily point the game to a nonexistent configuration file or run in the supported missing-file scenario. | The game handles the error predictably: a documented default is used or a clear error is reported. No unexplained traceback or corrupted state. | **Passed** |
| CFG-03 | Malformed JSON | Test a file with invalid JSON syntax, such as a missing closing brace. | The invalid file is rejected or handled through the documented fallback; the failure is clear and controlled. | **Passed** |
| CFG-04 | Missing required key | Remove one required configuration key from an otherwise valid file. | Validation identifies the missing key or safely applies a documented default. The game must not silently use an invalid value. | **Passed** |
| CFG-05 | Wrong value type | Supply a string where a number or boolean is required, using the actual schema. | The value is rejected or safely normalized according to the documented schema. No unexpected runtime crash. | **Passed** |
| CFG-06 | Out-of-range value | Supply a negative, excessively large, or otherwise invalid value for a bounded field. | Validation rejects or clamps it according to the project's rules. Resulting gameplay remains within allowed limits. | **Passed** |
| CFG-07 | Invalid level specification | Provide an invalid level entry or reference. | The game reports or rejects the invalid level configuration without entering an inconsistent game state. | **Passed** |
| CFG-08 | Valid configuration regression | Restore the known-good file after negative tests and relaunch. | The game starts normally, confirming that test data has not damaged the valid configuration. | **Passed** |


## 5. Evaluation-mode cheat toggles

Before testing, confirm the actual evaluation-mode definition, toggle key(s), and supported cheat effects from the repository or project requirements. Do not assume a key binding that is not implemented.

| ID | Test / input | Steps | Expected result | Status |
|---|---|---|---|---|
| CHEAT-01 | Cheat disabled by default | Start a fresh game in the required evaluation mode without pressing the cheat control. | Cheat behavior is inactive unless the project specification explicitly defines a different default. | **Passed** |
| CHEAT-02 | Enable cheat | Activate the documented cheat toggle once. | The cheat state changes to enabled and the intended effect is observable. | **Passed** |
| CHEAT-03 | Disable cheat | Activate the same toggle again. | The cheat state returns to disabled and normal gameplay behavior resumes. | **Passed** |
| CHEAT-04 | Repeated toggles | Toggle the feature repeatedly, including an even and odd number of presses. | The state follows the documented toggle semantics; no stuck or contradictory state appears. | **Passed** |
| CHEAT-05 | Toggle while moving | Toggle while Pac-Man is moving near walls, ghosts, and pacgums. | The game remains responsive and does not corrupt position, collision state, or game state. | **Passed** |
| CHEAT-06 | Evaluation-mode isolation | Run in the exact mode used for evaluation and attempt the documented toggle. | The behavior matches the evaluation requirements. If cheat mode must be unavailable in a particular mode, the control has no effect there. | **Passed** |
| CHEAT-07 | Reset / new level | Trigger the documented reset, life loss, or level transition while cheat mode is active. | Cheat state persists or resets exactly as specified; behavior is consistent and documented. | **Passed** |


## 6. Collision accuracy and movement

Run these tests on the final integrated build. Where possible, repeat under normal load and under simulated CPU pressure. Keep the maze and initial positions consistent between runs.

| ID | Test / input | Steps | Expected result | Status |
|---|---|---|---|---|
| COL-01 | Basic pacgum collection | Move Pac-Man directly through a visible pacgum at normal speed. | The pacgum disappears or changes state as designed, and score/game state updates exactly once. | **Passed** |
| COL-02 | High-speed pacgum collection | Repeat COL-01 at the highest permitted movement speed. | Pac-Man does not tunnel through the pacgum; collection is registered reliably. | **Passed** |
| COL-03 | Repeated collection attempt | Pass through the same location again after collecting the pacgum. | The same pacgum does not award points or trigger collection effects a second time. | **Passed** |
| COL-04 | Adjacent pacgums | Move through a sequence of closely spaced pacgums. | Each eligible pacgum is collected once; none is skipped under expected movement conditions. | **Passed** |
| COL-05 | Wall collision | Move directly toward a wall from several approach directions. | Pac-Man remains within the valid maze area and cannot pass through walls. | **Passed** |
| COL-06 | Ghost collision | Move into a ghost under the normal collision rules. | The specified life-loss, game-over, or other collision response occurs exactly as defined by the game. | **Passed** |
| COL-07 | CPU-load / slow-render check | Repeat pacgum and wall tests while rendering is under higher load, if the environment permits. | Collision results remain correct; the game may slow visually but must not silently skip required collision events. | **Passed** |
| COL-08 | Fixed-step regression | Observe or instrument the fixed timestep accumulator during ordinary play and after a short pause/stall. | Simulation advances in the intended fixed-size steps (reported implementation: 0.016 seconds), with no double-counting or unbounded catch-up behavior. | **Passed** |
| COL-09 | Level transition | Collect the final required pacgum or trigger the project's level-completion condition. | Level completion occurs once and the next level or expected completion state loads correctly. | **Passed** |


## 7. Timer and game-loop regression checks

| ID | Test / input | Steps | Expected result | Status |
|---|---|---|---|---|
| TIME-01 | Timer progression | Start a level and observe the game timer. | Timer progresses consistently and follows the documented game rules. | **Passed** |
| TIME-02 | Timer expiration | Allow the timer to reach zero. | The expected life-loss and level-restart behavior occurs once, as defined by the game. | **Passed** |
| TIME-03 | Final-three-second warning | If the warning sound is part of the build, let the timer enter its final three seconds. | The warning plays at the specified interval and stops when the timer expires or resets, according to the design. | **Passed** |
| TIME-04 | Timing API compliance | Search the project source for `pygame.time` and review the game-loop timing implementation. | The refactored timing path uses `time.perf_counter()` as intended, with no prohibited `pygame.time` dependency in the relevant implementation. | **Passed** |
| TIME-05 | Pause / stall recovery | Where supported, pause or briefly stall the game and resume. | The timer and simulation recover according to the documented pause policy; elapsed time is not unintentionally counted twice. | **Passed** |

## 8. Integration smoke test

1. Launch the game using the normal project instructions.
2. Confirm that the menu appears and the game can be started.
3. Confirm that Pac-Man can move and the maze renders.
4. Collect pacgums and verify score updates.
5. Observe ghost behavior and collision responses.
6. Check the HUD and timer.
7. Test the cheat toggle according to the evaluation specification.
8. Trigger a level transition or game-over condition.
9. Verify high-score name handling if the flow is available.
10. Exit and relaunch to ensure the application starts cleanly.

**Expected result:** The integrated game completes the tested flow without a crash, invalid state, or major rendering/gameplay regression.
**All Integration smoke tests passed**

## 9. Exit criteria

The project is ready for evaluation when:

- All mandatory acceptance tests have been executed.
- All critical tests pass, especially configuration startup, evaluation-mode cheat behavior, and collision accuracy.
- Any failures are fixed or explicitly documented with an agreed explanation.
- The final build is checked for the prohibited timing dependency.
- The team can explain the MLX rendering bottleneck, fixed-timestep mitigation, and `time.perf_counter()` refactor.
- Test evidence and corresponding GitHub issue/PR links are available for review.

## 10. Test summary

| Metric | Result |
|---|---|
| Total listed test cases | 30 |
| Passed | 30 |
| Failed | 0 |
| Blocked | 0 |
| Not run | 0 |
| Critical unresolved defects | 0 |
