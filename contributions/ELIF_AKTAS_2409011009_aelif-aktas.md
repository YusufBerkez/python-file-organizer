# Contribution – Arife Elif Aktaş
- **Student ID:** 2409011009
- **GitHub:** aelif-aktas
- **Role:** Episode detection (business logic) and statistics report
- **Branch:** `feature/episode-report`

## Files I wrote
- `episode.py`
- `report.py`

## What I implemented
- `split_words()` splits a file name into lower-case words at spaces, `_`, `-` and `.`.
- `to_number()`, `read_season_episode()` and `read_episode_number()` recognise `EP12`, `ep-012`, `Episode 12`, `Bolum_12` and `S02E05`; `extract_episode()` normalizes them to `EP012` / `S02E05` and rejects false matches such as `deep12`, episode 0 or 4-digit numbers.
- `group_by_episode()` and `find_missing()` list the required deliverables each episode is still missing.
- `build_statistics()` counts files and bytes per category and collects unique episode ids.
- `render_report()` builds the multi-line report; `format_size()` shows bytes as KiB/MiB/GiB.
- `save_report()` writes the report only to a new `.txt`/`.md` file, safely checking directory paths and preventing overwrites.

## Design decisions
- Season style is checked before episode style, so `S01E02` is never read as plain episode 2.
- A word must start with `ep`, so names like `deep12` are not treated as episodes.
- A set of present categories per episode makes the missing check simple and ignores duplicates.
- Raised specific exceptions (`ValueError`, `FileExistsError`, `NotADirectoryError`) in `save_report()` rather than failing silently, ensuring robust and safe file handling.

## Course topics I applied
- Looping over the characters of a string and building a list of words (W2)
- String methods `lower`, `split`, `startswith`, `join` (W3 S32-34)
- Accumulator pattern and stats dictionary (W2, W3 S59-61)
- `format_size` helper (W3 S58)
- f-strings, alignment, multi-line report (W3 S37-39)
- Sets for unique values, returning a tuple (W3 S19-20)
- `with open(..., "w")` for safe file writing (W2, W3 S49)
- Path and filesystem operations `os.path.splitext`, `os.path.split`, `os.path.lexists`, `os.path.isdir` (W3 S50-56)

## Commits
1. Add episode detection from file names
2. Add statistics report and size formatting
3. Add contribution file
