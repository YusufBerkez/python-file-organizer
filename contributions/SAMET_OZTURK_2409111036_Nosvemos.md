# Contribution – Samet Öztürk

- **Student ID:** 2409111036
- **GitHub:** Nosvemos
- **Role:** Safe file moving, dry-run plan and undo
- **Branch / Pull Request:** `feature/organizer` → feature/organizer

## Files I wrote
- `organizer.py`

## What I implemented
- `validate_paths()` checks source/destination (empty, same folder, destination is a file).
- `build_plan()` computes `<dest>/<episode>/<category>/<name>` for every file without touching the disk, so the same plan is used for preview and apply.
- `unique_target()` never overwrites: a taken name becomes `name (1).ext`, checked on disk and inside the plan (case-insensitive for Windows).
- `is_inside()` guarantees every target stays inside the destination.
- `move_file()` / `apply_plan()` move files with `shutil.move`, catch `FileNotFoundError` / `PermissionError` / `OSError` per file and keep going.
- A small text undo log (`.organizer_log.txt`, one `run<TAB>source<TAB>target` line per move); `undo_last_run()` previews or moves the last run back and removes the empty folders it created.

## Design decisions
- Planning and moving are separate functions: preview is the default and moving needs `--apply` (lecture organizer, W3 S65-66).
- The undo log is checked line by line before use and paths outside the destination are refused, so an edited log cannot move other files.
- `remove_empty_folders()` only deletes folders that are empty and stops at the destination folder.

## Course topics I applied
- `os.makedirs(exist_ok=True)`, `shutil.move`, `shutil.rmtree`, `os.remove` (W3 S53-55)
- `os.path.lexists` collision guard (W3 S56, S65)
- Preview before filesystem changes (W3 S65-66)
- `try/except FileNotFoundError / PermissionError / OSError` (W3 S67)
- Returning a tuple `(moved, failed)` (W3 S19)
- Reading and writing a text file with `with open` (W2)

## Commits
1. Add move planning with collision and path checks
2. Add safe moving, undo log and undo command
3. Add contribution file
