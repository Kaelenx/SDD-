# Task Plan: SDD Frontend-Backend Study Task Tracker

## Goal
Create a small, complete SDD-style frontend-backend web project with requirements documentation, technical plan, task traceability, runnable code, unit tests, browser verification, and a coverage report.

## Current Phase
Complete

## Phases

### Phase 1: Requirements & Discovery
- [x] Understand assignment acceptance criteria
- [x] Adjust project type to frontend-backend after user clarification
- [x] Keep the project scope small and reviewable
- **Status:** complete

### Phase 2: SDD Documentation
- [x] Rewrite `spec.md` for frontend-backend requirements
- [x] Rewrite `plan.md` for REST API and static frontend architecture
- [x] Rewrite `tasks.md` to map frontend, backend, tests, and docs
- **Status:** complete

### Phase 3: Implementation
- [x] Reuse domain, storage, and service layers
- [x] Replace CLI with REST backend and static file server
- [x] Add frontend HTML/CSS/JavaScript
- **Status:** complete

### Phase 4: Testing & Coverage
- [x] Update API tests
- [x] Run unit tests
- [x] Run coverage report
- **Status:** complete

### Phase 5: Browser Verification & Delivery
- [x] Start local web server
- [x] Verify frontend in browser
- [x] Update self-test report
- [x] Handoff URL and project summary
- **Status:** complete

### Phase 6: Feature Upgrade
- [x] Add backend task update API
- [x] Add search and priority filtering
- [x] Add frontend edit mode and completion progress
- [x] Run tests and browser verification
- [x] Update final report
- **Status:** complete

## Key Questions
1. What frontend-backend project is small enough to finish while showing full SDD lifecycle?
   - A study task tracker web app is appropriate: clear CRUD behavior, API boundary, persistence, and testable errors.
2. How can the backend run without external dependencies?
   - Use Python standard-library `http.server`.
3. How will the frontend interact with the backend?
   - Use `fetch('/api/...')` from static HTML/CSS/JS served by the same Python server.

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Convert the CLI project to a frontend-backend web app | User clarified that the expected type is frontend-backend |
| Keep Python standard library only | Reduces dependency and evaluation risk |
| Use REST + JSON | Clear frontend/backend contract |
| Serve frontend and API from the same local server | Simplifies local running and avoids CORS issues |
| Keep JSON persistence | Sufficient for a small single-user project |
| Add edit/search/priority/progress features | Makes the project more convincingly frontend-backend without adding external dependencies |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| Initial delivery was CLI-style rather than frontend-backend | 1 | Converted project to REST backend plus static frontend |
| First coverage script design was too slow | 1 | Replaced broad tracing with source-only `sys.settrace` |
| Coverage timed out after feature upgrade | 2 | Cached normalized filenames and used string path matching |

## Notes
- Assignment requires `spec.md`, `plan.md`, tasks, code, unit tests, and normal run verification in one root folder.
- The final deliverable should open in a browser and still pass backend tests.
