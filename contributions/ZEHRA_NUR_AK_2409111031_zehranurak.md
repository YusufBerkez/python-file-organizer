# Contribution – Zehra Nur Ak

- **Student ID:** 2409111031
- **GitHub:** zehranurak
- **Role:** File scanner and type classification (core organizer)
- **Branch / Pull Request:** `feature/scanner` → feature/scanner

## Files I wrote
- `scanner.py`

## What I implemented
- `normalize_extension()` / `get_extension()`: lower-case, remove the dot, merge aliases such as `jpeg → jpg`.
- `should_skip()` skips dot-files, OS junk (`desktop.ini`, `Thumbs.db`, `.DS_Store`) and names the undo log cannot store.
- `validate_directory()` rejects empty paths and missing folders.
- `scan_directory()` lists only regular files (no sub-folders, no symbolic links), limits a run to 10,000 files and returns one record dictionary per file.
- `assign_categories()` gives each record its category with `extension_map.get(ext, other_folder)`.

## Design decisions
- Scanning never changes the disk; it only produces records, so preview and apply use exactly the same data.
- Links are skipped because a link could point outside the inbox.
- Files that disappear or are locked during the scan are skipped instead of crashing the run.

## Course topics I applied
- `os.listdir`, `os.path.join`, `os.path.splitext`, `isfile`, `islink`, `getsize` (W3 S50-53, S60)
- Extension normalization exercise (W3 S35-36, S57)
- Lists, `for` loops, `sorted()` (W2)
- Dictionary lookup with a default (W3 S17, S63)
- String methods `strip`, `lower`, `startswith` (W3 S32-33)

## Commits
1. Add extension helpers and folder validation
2. Add directory scanning and category assignment
3. Add contribution file
