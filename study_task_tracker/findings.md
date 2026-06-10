# Findings & Decisions

## Requirements
- Create a project that follows SDD standard process.
- Include standard documents and final self-tested/debugged code.
- `spec.md` must clarify requirements, business boundaries, and abnormal boundaries.
- `plan.md` must define architecture and technical dependencies.
- Task phase must match final code; task completeness must be visible.
- Include unit tests and a unit test coverage result.
- Project must run normally.
- User clarified the project should be frontend-backend type.

## Research Findings
- Current workspace started empty and not as a Git repository, so a self-contained folder is the safest delivery shape.
- Python 3.12.12 is available.
- Third-party coverage tools are not confirmed, so the project should avoid external runtime/test dependencies.
- Python standard library can provide a small REST/static server through `http.server`.
- Final verification after feature upgrade: 29 tests passed; source coverage is 85.3%; browser add/search/filter/edit/complete flow passed on `http://127.0.0.1:8765`.
- Feature upgrade added task editing, keyword search, priority filtering, and completion progress while keeping the no-dependency architecture.
- Complexity upgrade added task notes, estimated hours, course statistics, bulk completion, and export.
- Engineering upgrade split backend into domain/application/infrastructure/web and split frontend into native ES modules.

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Project folder: `study_task_tracker` | Clear assignment delivery folder at workspace root |
| Frontend: HTML/CSS/JS | Zero build step and visible browser UI |
| Backend: Python `http.server` | Standard library, simple REST API |
| API: REST + JSON | Clear frontend/backend separation |
| Storage: JSON file | Simple persistent storage for a small project |
| Tests: `unittest` + API server tests | Standard library and verifies backend contract |
| Edit/search/filter features | Adds useful complexity while keeping the code reviewable |
| Course stats and batch operations | Demonstrates richer backend aggregation and frontend state management |
| Backend compatibility wrappers | Preserve reviewer-facing commands while improving internal structure |
| Native frontend modules | Improve maintainability without adding Node or build dependencies |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| Initial project type was CLI | Converted to frontend-backend web app |
| Initial coverage script used broad tracing and timed out once | Replaced with source-only `sys.settrace` |
| Server code ran in another thread and was initially undercounted by coverage | Added `threading.settrace` |
| Port 8000 was blocked on this Windows machine | Changed default port to 8765 |

## Resources
- Python available locally: Python 3.12.12
- Project root: `E:\Project_Code\Codex\SD\study_task_tracker`

## Visual/Browser Findings
- Browser rendered the frontend page title, summary area, form, filters, and empty task state.
- Adding a task through the form created T0001 and updated summary to total=1, pending=1.
- Completing the task updated the card to done and summary to done=1, pending=0.
- Browser console error log was empty.
- After cleanup and reload, page showed empty state and all summary counts were 0.
- After feature upgrade, browser verified keyword search, high-priority filtering, edit-save flow, task completion, and 50% completion progress.
- Complexity verification covered notes, estimated hours, course statistics, bulk completion, stale selection fix, and no browser console errors.
- Engineering verification confirmed module loading, task creation, summary refresh, course refresh, and no browser console errors.
