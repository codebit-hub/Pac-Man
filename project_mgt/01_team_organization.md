# Team Organization

## 1. Project overview

The team 'Ghost Runners', consisting of two teammates, namely dporhomo and vokatera, have implemented the Pac-Man game project as part of a 42 school coding curriculum. The planned delivery window was four weeks. The team completed the implementation in 22 days, leaving six days for evaluation preparation.

| Team member | Main responsibility | Scope |
|---|---|---|
| `dporhomo` | Project Management and Back-end with game logic | Player and ghost logic, maze loading, game state, scoring, configuration, difficulty, timers, and gameplay rules |
| `vokatera` | Front-end and rendering | UI, menu, HUD, renderer, audio, and visual integration |
| Both | Shared integration and delivery | Shared entry point (`pac_man.py`), README, cross-component integration, bug fixing, and evaluation preparation |

These were the primary areas of ownership, not isolated silos. Shared files and integration points required coordination and review by both team members.

## 2. GitHub workflow

GitHub Issues and pull requests were used to track work and integrate changes.

### Issue tracking

- Work was represented by GitHub Issues with a clear task description and an identifiable owner.
- Issues were closed when the corresponding work was completed and integrated.
- The project closed 20 issues during the implementation period.
- Issues covered setup, core game logic, difficulty and level rules, rendering and audio, shared files, and final gameplay features.

### Branch strategy

The team used development branches:

- `Front-end-dev` — front-end and rendering work.
- `Back-end-dev` — back-end and game-logic work.

A practical workflow was:

1. Identify or create an issue for a task.
2. Implement the change in the appropriate development branch.
3. Review the change for compatibility with the other side of the game.
4. Integrate the change through a pull request or agreed GitHub integration process.
5. Run relevant checks and a gameplay smoke test.
6. Close the issue once the work was integrated and verified.

The branches reflected responsibility boundaries. Shared files such as `pac_man.py` and `README` required particular care because changes could affect both sides.


## 3. Communication and coordination

The team coordinated around component boundaries and integration dependencies.

- **Ownership:** Each team member focused primarily on their assigned area to reduce conflicting edits.
- **Integration:** Front-end and back-end changes were checked together, especially where the renderer, game loop, timers, and shared entry point interacted.
- **Blocking points:** Technical problems affecting both components were treated as integration risks rather than as isolated implementation details.
- **Change communication:** Changes to shared files, timing behavior, configuration, or interfaces needed to be communicated to the other team member before integration.
- **Verification:** A feature was not considered complete solely because its code existed; the integrated game needed to remain playable.

## 4. Definition of done

A task was considered ready to close when applicable conditions were met:

- The implementation matched the issue's intended behavior.
- The change was integrated into the relevant development branch.
- It did not introduce an obvious regression in the integrated game.
- Relevant configuration, gameplay, or UI behavior was checked.
- Any important limitations or follow-up work were recorded.

## 5. Delivery outcome

The implementation was completed in 22 days of the four-week schedule, leaving six days for evaluation preparation. The final scope included the back-end game systems, front-end UI and rendering, shared project files, difficulty and level behavior, a cheat mode, and high-score name specification.
