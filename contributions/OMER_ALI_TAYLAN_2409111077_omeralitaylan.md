# Contribution – Ömer Ali Taylan

- **Student ID:** 2409111077
- **GitHub:** [omeralitaylan](https://github.com/omeralitaylan)
- **Role:** Configuration system and demo data
- **Branch:** `feature/config`

## Files I wrote
- `config.txt`
- `config_loader.py`
- `sample.py`

## What I implemented
- `config.txt`: a plain text config with `[categories]` (folder = extensions) and `[settings]` (required deliverables, folder names) that anyone can edit in Notepad.
- `read_config_lines()` reads the file with `with open(..., encoding="utf-8")` and turns a missing file, a file that is too big or not UTF-8 into a clear `ValueError`.
- `parse_config()` reads the file line by line, skips comments, understands sections and `name = value` lines and reports errors with the line number.
- `add_category()` inverts `Video = mp4, mov` into `{"mp4": "Video", "mov": "Video"}` so the scanner can use one `.get()` lookup.
- Validation of every value: folder names are whitelisted character by character, Windows reserved names are refused, an extension cannot be in two categories, required categories must exist.
- `sample.py` creates a disposable demo inbox with every naming style; the last episode has no subtitle on purpose so the report has something to show.

## Design decisions
- The config is treated as untrusted input: a category named `../../Windows` would otherwise create folders outside the destination, so I used a whitelist (allowed characters) instead of a blacklist.
- Plain text instead of a special format, so the tool only needs what we learned in class (`open`, `strip`, `split`).
- The demo command refuses to write into a folder that is not empty, so it can never mix fake files with real ones.

## Course topics I applied
- Dictionaries, `.get()`, sets (W3 S13-17, S20)
- `with open` and reading a file line by line (W2, W3 S49)
- String methods `strip`, `split`, `startswith`, `endswith`, `lower` (W3 S32-34)
- `try/except` with specific exceptions (W3 S67)
- Returning a tuple (W3 S19)
- Disposable test files (W3 S68)

## Commits
1. Add default category config for podcast files
2. Add config loader with validation
3. Add demo inbox generator
4. Add contribution file
